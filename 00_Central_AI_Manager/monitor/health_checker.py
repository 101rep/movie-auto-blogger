import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict
from config import settings
from adapters.registry import registry
from security.audit import audit_logger
from monitor.daily_reporter import daily_reporter

def _get_bot():
    from telegram_bot.bot import telegram_bot
    return telegram_bot

KST = timezone(timedelta(hours=9))

class RealTimeHealthMonitor:
    """Monitors all registered adapters, server resource limits, and runs daily briefing schedules."""

    def __init__(self) -> None:
        self.interval = settings.MONITOR_INTERVAL_SECONDS or 60
        self.is_running = False
        self._last_state: Dict[str, bool] = {}
        self._server_resource_alerted: bool = False

    async def start(self) -> None:
        self.is_running = True
        print(f"[HealthMonitor] 24시간 실시간 장애 감지 및 브리핑 스케줄러 시작됨 (주기: {self.interval}초)")
        
        while self.is_running:
            try:
                # 1. Check services and handle self-healing
                await self._run_check_cycle()
                
                # 2. Check server resources (RAM / Disk)
                await self._check_server_resources()

                # 3. Check daily 09:00 KST briefing schedule
                await daily_reporter.check_and_send_scheduled(_get_bot(), settings.TELEGRAM_ADMIN_CHAT_ID)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[HealthMonitor Cycle Error] {e}")

            await asyncio.sleep(self.interval)

    async def _run_check_cycle(self) -> None:
        SERVER_DAEMONS = {"cloudways_server", "multisite_blogger", "threads_coupang"}
        adapters = registry.get_all()
        for adapter in adapters:
            name = adapter.name
            # Only monitor 24/7 server daemons for active alerts and auto self-healing
            if name not in SERVER_DAEMONS:
                continue

            prev_healthy = self._last_state.get(name, True)
            
            try:
                curr_healthy = await adapter.health_check()
            except Exception:
                curr_healthy = False

            # State Transition: Healthy -> Down
            if prev_healthy and not curr_healthy:
                print(f"[HealthMonitor ALERT] Service DOWN: {name}")
                audit_logger.log("SYSTEM", f"alert_down_{name}", 2, "FAILURE", {"adapter": name})
                
                now_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")
                alert_msg = (
                    f"🚨 <b>[긴급 시스템 장애 감지]</b>\n\n"
                    f"• <b>대상 서비스</b>: <code>{adapter.description}</code>\n"
                    f"• <b>장애 시각</b>: {now_str}\n"
                    f"• <b>상태</b>: 응답 없음 (OFFLINE)\n\n"
                    f"⚡ <b>스스로 자동 자가 치유(Self-Healing)를 가동합니다...</b>"
                )
                await _get_bot().send_message(settings.TELEGRAM_ADMIN_CHAT_ID, alert_msg)
                
                # Auto Self-Healing Attempt
                try:
                    restart_res = await adapter.restart()
                    await asyncio.sleep(6)
                    recovered = await adapter.health_check()
                    if recovered:
                        curr_healthy = True
                        rec_msg = (
                            f"✅ <b>[자동 복구 완료 (Self-Healing)]</b>\n\n"
                            f"• <b>서비스</b>: <code>{adapter.description}</code>\n"
                            f"• <b>결과</b>: 자동 재기동을 통해 정상 복구되었습니다."
                        )
                        await _get_bot().send_message(settings.TELEGRAM_ADMIN_CHAT_ID, rec_msg)
                except Exception as ex:
                    print(f"[HealthMonitor Recovery Error] {ex}")

            # State Transition: Down -> Recovered
            elif not prev_healthy and curr_healthy:
                print(f"[HealthMonitor INFO] Service RECOVERED: {name}")
                audit_logger.log("SYSTEM", f"alert_recovered_{name}", 1, "SUCCESS", {"adapter": name})
                rec_msg = (
                    f"✅ <b>[시스템 정상 가동 확인]</b>\n\n"
                    f"• <b>대상 서비스</b>: <code>{adapter.description}</code>\n"
                    f"• <b>현재 상태</b>: 정상 작동 중 (ONLINE)"
                )
                await _get_bot().send_message(settings.TELEGRAM_ADMIN_CHAT_ID, rec_msg)

            self._last_state[name] = curr_healthy

    async def _check_server_resources(self) -> None:
        """Alert if RAM or Disk usage exceeds 92% threshold."""
        cw = registry.get("cloudways_server")
        if not cw:
            return

        try:
            status = await cw.get_status()
            details = status.details or {}
            mem = details.get("memory", {})
            disk = details.get("disk", {})

            # Disk check
            use_pct_str = disk.get("use_percent", "0%").replace("%", "").strip()
            use_pct = int(use_pct_str) if use_pct_str.isdigit() else 0

            # Memory check
            total_mb = mem.get("total_mb", 1)
            avail_mb = mem.get("available_mb", 1)
            mem_pct = int(((total_mb - avail_mb) / total_mb) * 100) if total_mb > 0 else 0

            if (use_pct > 92 or mem_pct > 92) and not self._server_resource_alerted:
                self._server_resource_alerted = True
                warn_msg = (
                    f"⚠️ <b>[서버 자원 임계치 주의 경보]</b>\n\n"
                    f"• <b>메모리 사용률</b>: {mem_pct}%\n"
                    f"• <b>디스크 사용률</b>: {use_pct}%\n"
                    f"• <b>권장 조치</b>: 불필요한 캐시 또는 로그 정리가 필요할 수 있습니다."
                )
                await _get_bot().send_message(settings.TELEGRAM_ADMIN_CHAT_ID, warn_msg)
            elif use_pct <= 85 and mem_pct <= 85:
                self._server_resource_alerted = False
        except Exception:
            pass

    def stop(self) -> None:
        self.is_running = False

health_monitor = RealTimeHealthMonitor()
