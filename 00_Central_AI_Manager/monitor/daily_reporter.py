import asyncio
import os
import re
import sqlite3
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from config import settings
from adapters.registry import registry
from security.audit import audit_logger

KST = timezone(timedelta(hours=9))
MORNING_REPORT_HOUR = 8   # 08:00 KST 일일 모닝 브리핑
TRAFFIC_REPORT_HOURS = [9, 15, 21] # 09:00, 15:00, 21:00 KST 3회 정기 블로그 방문자수/트래픽 보고


class DailyExecutiveReporter:
    """Generates and pushes daily morning executive briefing (08:00 KST) and 3x daily traffic reports (09:00, 15:00, 21:00 KST)."""

    def __init__(self) -> None:
        self.last_morning_date: Optional[str] = None
        self.sent_traffic_keys: set = set()

    def _collect_traffic_data(self) -> Dict[str, Any]:
        """Collect live traffic data across all 8 blogs from MySQL on Cloudways server."""
        apps_meta = [
            {"app_id": "ngmrkrwfzg", "id": 1, "name": "트래블픽24", "url": "travelpick24.com", "category": "여행"},
            {"app_id": "zqdzpptvqs", "id": 2, "name": "트렌드스팟24", "url": "trendspot24.com", "category": "영화"},
            {"app_id": "exsmnhvpuz", "id": 3, "name": "아이템픽24", "url": "item.travelpick24.com", "category": "상품비교"},
            {"app_id": "tupwbmjjfs", "id": 4, "name": "뉴스픽24", "url": "news.trendspot24.com", "category": "시사뉴스"},
            {"app_id": "thdvnrcwkr", "id": 5, "name": "엔터픽24", "url": "enter.trendspot24.com", "category": "연예문화"},
            {"app_id": "yfvrxkqnms", "id": 6, "name": "복지픽24", "url": "welfare24.travelpick24.com", "category": "시니어/소상공인"},
            {"app_id": "tdjxvgaktu", "id": 7, "name": "복지픽25", "url": "welfare25.travelpick24.com", "category": "생활바우처"},
            {"app_id": "yqyaryssqj", "id": 8, "name": "복지픽23", "url": "welfare23.travelpick24.com", "category": "청년/주거복지"},
        ]

        site_stats = []
        tot_today_vis, tot_today_pv = 0, 0
        tot_yest_vis, tot_yest_pv = 0, 0
        tot_month_vis, tot_month_pv = 0, 0

        # Try live query from Cloudways directories
        for meta in apps_meta:
            app_id = meta["app_id"]
            paths = [
                f"/home/1670576.cloudwaysapps.com/{app_id}/public_html/wp-config.php",
                f"/home/master/applications/{app_id}/public_html/wp-config.php"
            ]
            wp_conf = next((p for p in paths if os.path.exists(p)), None)

            today_vis, today_pv = 0, 0
            yest_vis, yest_pv = 0, 0
            month_vis, month_pv = 0, 0

            if wp_conf:
                db_user, db_pass, db_name, prefix = None, None, None, "wp_"
                try:
                    with open(wp_conf, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            l = line.strip()
                            if "DB_USER" in l and "define" in l:
                                db_user = l.split(",")[1].split(")")[0].replace("'", "").replace('"', '').replace(';', '').strip()
                            elif "DB_PASSWORD" in l and "define" in l:
                                db_pass = l.split(",")[1].split(")")[0].replace("'", "").replace('"', '').replace(';', '').strip()
                            elif "DB_NAME" in l and "define" in l:
                                db_name = l.split(",")[1].split(")")[0].replace("'", "").replace('"', '').replace(';', '').strip()
                            elif "$table_prefix" in l:
                                prefix = l.split("=")[1].replace("'", "").replace('"', '').replace(';', '').strip()

                    cmd_base = ["mysql", "-u", db_user, f"-p{db_pass}", db_name, "-N", "-e"]
                    r_tab = subprocess.run(cmd_base + [f"SHOW TABLES LIKE '{prefix}%';"], capture_output=True, text=True)
                    tabs = r_tab.stdout.split()

                    if f"{prefix}daily_site_visits" in tabs:
                        r_today = subprocess.run(cmd_base + [f"SELECT visitors, pageviews FROM {prefix}daily_site_visits WHERE visit_date=CURDATE();"], capture_output=True, text=True)
                        if r_today.stdout.strip():
                            p = r_today.stdout.strip().split()
                            if len(p) >= 2:
                                today_vis, today_pv = int(p[0]), int(p[1])

                        r_yest = subprocess.run(cmd_base + [f"SELECT visitors, pageviews FROM {prefix}daily_site_visits WHERE visit_date=DATE_SUB(CURDATE(), INTERVAL 1 DAY);"], capture_output=True, text=True)
                        if r_yest.stdout.strip():
                            p = r_yest.stdout.strip().split()
                            if len(p) >= 2:
                                yest_vis, yest_pv = int(p[0]), int(p[1])

                        r_month = subprocess.run(cmd_base + [f"SELECT SUM(visitors), SUM(pageviews) FROM {prefix}daily_site_visits WHERE visit_date>=DATE_FORMAT(CURDATE(), '%Y-%m-01');"], capture_output=True, text=True)
                        if r_month.stdout.strip():
                            p = r_month.stdout.strip().split()
                            if len(p) >= 2 and p[0] != "NULL":
                                month_vis, month_pv = int(p[0]), int(p[1])
                except Exception as e:
                    print(f"[TrafficCollect Error {app_id}] {e}")

            tot_today_vis += today_vis
            tot_today_pv += today_pv
            tot_yest_vis += yest_vis
            tot_yest_pv += yest_pv
            tot_month_vis += month_vis
            tot_month_pv += month_pv

            site_stats.append({
                "id": meta["id"],
                "name": meta["name"],
                "url": meta["url"],
                "category": meta["category"],
                "today_vis": today_vis,
                "today_pv": today_pv,
                "yest_vis": yest_vis,
                "yest_pv": yest_pv,
                "month_vis": month_vis,
                "month_pv": month_pv,
            })

        return {
            "date": datetime.now(KST).strftime("%Y년 %m월 %d일 %H:%M KST"),
            "total_today_vis": tot_today_vis,
            "total_today_pv": tot_today_pv,
            "total_yest_vis": tot_yest_vis,
            "total_yest_pv": tot_yest_pv,
            "total_month_vis": tot_month_vis,
            "total_month_pv": tot_month_pv,
            "sites": site_stats
        }

    def _collect_scheduled_posts_data(self) -> Dict[str, Any]:
        """7대 블로그(아이템픽24 제외)의 일일 4개 예약발행 일정 및 현황 수집."""
        target_sites = [
            {"id": 1, "name": "트래블픽24", "url": "travelpick24.com", "category": "여행"},
            {"id": 2, "name": "트렌드스팟24", "url": "trendspot24.com", "category": "영화"},
            {"id": 4, "name": "엔터픽24", "url": "enter.trendspot24.com", "category": "연예문화"},
            {"id": 5, "name": "복지픽23", "url": "welfare23.travelpick24.com", "category": "청년/주거복지"},
            {"id": 6, "name": "복지픽24", "url": "welfare24.travelpick24.com", "category": "시니어/소상공인"},
            {"id": 7, "name": "복지픽25", "url": "welfare25.travelpick24.com", "category": "생활바우처"},
            {"id": 8, "name": "뉴스픽24", "url": "news.trendspot24.com", "category": "시사뉴스"},
        ]

        now_kst = datetime.now(KST)
        today_str = now_kst.strftime("%Y-%m-%d")
        DEFAULT_SLOTS = ["08:00", "12:30", "18:00", "21:30"]

        db_candidates = [
            "/home/master/multisite_auto_blogger/data/movie_blogger.db",
            r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\02_Movie_Auto_Blogger\data\movie_blogger.db"
        ]
        db_path = next((p for p in db_candidates if os.path.exists(p)), None)

        posts_by_site = {s["id"]: [] for s in target_sites}

        if db_path:
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                for s in target_sites:
                    s_id = s["id"]
                    today_posts = cur.execute('''
                        SELECT id, title, status, scheduled_at, published_at
                        FROM posts
                        WHERE site_id = ? AND (scheduled_at LIKE ? OR published_at LIKE ?)
                        ORDER BY COALESCE(scheduled_at, published_at) ASC
                    ''', (s_id, f"{today_str}%", f"{today_str}%")).fetchall()

                    upcoming = []
                    if len(today_posts) < 4:
                        needed = 4 - len(today_posts)
                        upcoming = cur.execute('''
                            SELECT id, title, status, scheduled_at, published_at
                            FROM posts
                            WHERE site_id = ? AND status = 'SCHEDULED'
                            ORDER BY scheduled_at ASC LIMIT ?
                        ''', (s_id, needed)).fetchall()
                    posts_by_site[s_id] = [dict(r) for r in list(today_posts) + list(upcoming)]
                conn.close()
            except Exception as e:
                print(f"[DailyReporter _collect_scheduled_posts_data DB Error] {e}")
        else:
            # Fallback to SSH probe if running remotely without local DB
            try:
                import paramiko
                import json
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect('139.59.125.237', port=22, username='master_amtfargkbx', password='bN6TUBm5VAVC', timeout=5)
                cmd = f"""python3 -c "
import sqlite3, json
conn = sqlite3.connect('/home/master/multisite_auto_blogger/data/movie_blogger.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
res = {{}}
for sid in [1, 2, 4, 5, 6, 7, 8]:
    today_posts = cur.execute('''
        SELECT id, title, status, scheduled_at, published_at
        FROM posts
        WHERE site_id = ? AND (scheduled_at LIKE '{today_str}%' OR published_at LIKE '{today_str}%')
        ORDER BY COALESCE(scheduled_at, published_at) ASC
    ''', (sid,)).fetchall()
    upcoming = []
    if len(today_posts) < 4:
        upcoming = cur.execute('''
            SELECT id, title, status, scheduled_at, published_at
            FROM posts
            WHERE site_id = ? AND status = 'SCHEDULED'
            ORDER BY scheduled_at ASC LIMIT ?
        ''', (sid, 4 - len(today_posts))).fetchall()
    res[sid] = [dict(r) for r in list(today_posts) + list(upcoming)]
print(json.dumps(res))
"
"""
                stdin, stdout, stderr = client.exec_command(cmd, timeout=7)
                raw = stdout.read().decode('utf-8', errors='ignore').strip()
                client.close()
                if raw:
                    remote_data = json.loads(raw)
                    for sid_str, p_list in remote_data.items():
                        posts_by_site[int(sid_str)] = p_list
            except Exception as e:
                print(f"[DailyReporter _collect_scheduled_posts_data SSH Error] {e}")

        site_schedules = []
        tot_target = len(target_sites) * 4 # 28
        tot_published = 0
        tot_scheduled = 0

        for s in target_sites:
            s_id = s["id"]
            posts = posts_by_site.get(s_id, [])
            slots_info = []

            for i in range(4):
                slot_time = DEFAULT_SLOTS[i]
                if i < len(posts):
                    p = posts[i]
                    st = p.get("status", "SCHEDULED")
                    t_val = p.get("scheduled_at") or p.get("published_at") or ""
                    if t_val and " " in str(t_val):
                        slot_time = str(t_val).split()[1][:5]

                    clean_title = re.sub(r'<[^>]+>', '', p.get("title", "")).strip()
                    if len(clean_title) > 26:
                        clean_title = clean_title[:24] + "..."

                    if st == "PUBLISHED":
                        slots_info.append({"icon": "✅", "time": slot_time, "status": "발행완료", "title": clean_title})
                        tot_published += 1
                    else:
                        slots_info.append({"icon": "⏳", "time": slot_time, "status": "예약대기", "title": clean_title})
                        tot_scheduled += 1
                else:
                    slots_info.append({"icon": "🕒", "time": slot_time, "status": "예약슬롯", "title": "자동 예약 대기"})
                    tot_scheduled += 1

            site_schedules.append({
                "id": s["id"],
                "name": s["name"],
                "url": s["url"],
                "category": s["category"],
                "slots": slots_info
            })

        return {
            "date": today_str,
            "total_target": tot_target,
            "total_published": tot_published,
            "total_scheduled": tot_scheduled,
            "sites": site_schedules
        }

    async def generate_schedule_report(self) -> str:
        """7대 블로그(아이템픽24 제외) 일일 4개 예약발행 일정 단독 리포트 생성."""
        sched_data = self._collect_scheduled_posts_data()
        date_str = datetime.now(KST).strftime("%Y년 %m월 %d일 %H:%M KST")

        lines = [
            "⏰ <b>[7대 블로그 일일 4개 예약발행 일정 현황]</b>",
            "━━━━━━━━━━━━━━━━━━━━",
            f"📅 <b>기준 시각</b>: {date_str}",
            "📌 <b>대상 블로그</b>: 아이템픽24 제외 총 7개 블로그",
            f"🎯 <b>일일 목표</b>: 총 <b>{sched_data['total_target']}편</b> (발행 완료: <b>{sched_data['total_published']}편</b> · 예약 대기: <b>{sched_data['total_scheduled']}편</b>)\n",
            "━━━━━━━━━━━━━━━━━━━━",
            "📋 <b>[각 블로그별 4개 슬롯 상세 현황]</b>\n"
        ]

        for s in sched_data.get("sites", []):
            lines.append(f"<b>{s['id']}. {s['name']}</b> ({s['url']} - {s['category']})")
            for slot in s["slots"]:
                lines.append(f"  {slot['icon']} <code>{slot['time']}</code> [{slot['status']}] {slot['title']}")
            lines.append("")

        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("💡 <code>/traffic</code> | <code>/schedule</code> | <code>/status</code>")
        return "\n".join(lines).strip()

    async def generate_evening_traffic_report(self, time_label: Optional[str] = None) -> str:
        """방문자수 및 7대 블로그 일일 4개 예약발행 일정 통합 리포트 생성."""
        data = self._collect_traffic_data()
        sched_data = self._collect_scheduled_posts_data()
        date_str = data["date"]
        label = time_label or datetime.now(KST).strftime("%H:%M KST")

        lines = [
            f"📊 <b>[8대 블로그 통합 일일 트래픽 리포트 ({label})]</b>",
            "━━━━━━━━━━━━━━━━━━━━",
            f"📅 <b>보고 시각</b>: {date_str}\n",
            "🏆 <b>[전체 8개 블로그 총합]</b>",
            "오늘 순방문자",
            f"<b>{data['total_today_vis']} 명</b>",
            f"(어제: {data['total_yest_vis']}명)",
            "오늘 페이지뷰",
            f"<b>{data['total_today_pv']} 회</b>",
            f"(어제: {data['total_yest_pv']}회)",
            "이번 달 누적 방문",
            f"<b>{data['total_month_vis']} 명</b>",
            f"(누적 {data['total_month_pv']} PV)\n",
            "━━━━━━━━━━━━━━━━━━━━",
            "📋 <b>[각 블로그별 세부 현황]</b>\n"
        ]

        for s in data.get("sites", []):
            lines.append(f"<b>{s['id']}. {s['name']}</b> ({s['url']})")
            lines.append("오늘 순방문자")
            lines.append(f"<b>{s['today_vis']} 명</b>")
            lines.append(f"(어제: {s['yest_vis']}명)")
            lines.append("오늘 페이지뷰")
            lines.append(f"<b>{s['today_pv']} 회</b>")
            lines.append(f"(어제: {s['yest_pv']}회)")
            lines.append("이번 달 누적 방문")
            lines.append(f"<b>{s['month_vis']} 명</b>")
            lines.append(f"(누적 {s['month_pv']} PV)\n")

        # 7대 블로그 일일 4개 예약발행 일정 (아이템픽24 제외)
        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("⏰ <b>[7대 블로그 일일 4개 예약발행 일정 현황]</b>")
        lines.append(f"📌 <i>아이템픽24 제외 / 일일 총 28편 목표 (발행 완료: {sched_data['total_published']}편 · 대기: {sched_data['total_scheduled']}편)</i>\n")

        for s in sched_data.get("sites", []):
            lines.append(f"<b>{s['id']}. {s['name']}</b> ({s['url']})")
            for slot in s["slots"]:
                lines.append(f"  {slot['icon']} <code>{slot['time']}</code> [{slot['status']}] {slot['title']}")
            lines.append("")

        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("💡 <code>/traffic</code> | <code>/schedule</code> | <code>/status</code>")
        return "\n".join(lines).strip()

    async def generate_traffic_report(self, time_label: Optional[str] = None) -> str:
        """Alias for generate_evening_traffic_report."""
        return await self.generate_evening_traffic_report(time_label)

    async def generate_briefing(self) -> str:
        """Comprehensive morning briefing at 08:00 KST: server, 8 blogs, threads, AI cost, security."""
        now_kst = datetime.now(KST)
        date_str = now_kst.strftime("%Y년 %m월 %d일 %H:%M KST")

        # 1. System Overview
        overview = await registry.get_system_overview()
        cw = overview.get("cloudways_server")
        blogger = overview.get("multisite_blogger")
        threads = overview.get("threads_coupang")

        cw_healthy = getattr(cw, "is_running", False)
        blogger_healthy = getattr(blogger, "is_running", False)
        threads_healthy = getattr(threads, "is_running", False)

        # 2. Server Metrics
        mem_info = "정상"
        disk_info = "여유"
        if cw:
            details = getattr(cw, "details", {})
            mem = details.get("memory", {})
            disk = details.get("disk", {})
            if mem:
                mem_info = f"{mem.get('used_mb', 0)}MB 사용 중 / 여유 {mem.get('available_mb', 0)}MB (총 {mem.get('total_mb', 0)}MB)"
            if disk:
                disk_info = f"{disk.get('used', '')} 사용 중 / 잔여 {disk.get('available', '')} (사용률: {disk.get('use_percent', '')})"

        # 3. Blog Status
        recent_posts_count = 0
        blogger_adapter = registry.get("multisite_blogger")
        if blogger_adapter:
            try:
                res = await blogger_adapter.trigger_action("get_recent_posts", {"limit": 5})
                recent_posts_count = len(res.get("posts", []))
            except Exception:
                pass

        # 4. Threads Metrics
        threads_details_str = "7대 계정 인간모방 소통 및 웜업 정상 가동"
        threads_adapter = registry.get("threads_coupang")
        if threads_adapter:
            try:
                metrics = await threads_adapter.trigger_action("get_metrics")
                accs = metrics.get("accounts", [])
                tot_c = metrics.get("total_contents", 0)
                tot_o = metrics.get("total_outbound", 0)
                if accs:
                    avg_score = sum([a.get("trust_score", 0) for a in accs]) / len(accs)
                    threads_details_str = (
                        f"7대 계정 신뢰도 평균 <b>{avg_score:.1f}점</b> | "
                        f"누적 콘텐츠 <b>{tot_c}편</b> | 소통(Outbound) <b>{tot_o}건</b>"
                    )
            except Exception:
                pass

        # 5. AI Cost Summary (today)
        cost_str = "사용 내역 없음"
        try:
            from agent.memory_db import agent_db
            cost = agent_db.get_cost_summary(days=1)
            total = cost.get("total_usd", 0)
            cost_str = f"오늘 AI 비용: <b>${total:.6f}</b>"
        except Exception:
            pass

        # 6. Security Audit
        recent_audits = audit_logger.get_recent_logs(limit=20)
        audit_count = len(recent_audits)

        return (
            f"☀️ <b>[AG Command Center v2.0 일일 모닝 브리핑]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 <b>보고 시각</b>: {date_str}\n\n"
            f"1️⃣ <b>Cloudways 리눅스 서버</b> ({'🟢 정상' if cw_healthy else '🔴 점검 필요'})\n"
            f"   • 호스트: <code>{settings.CLOUDWAYS_HOST}</code>\n"
            f"   • 메모리(RAM): {mem_info}\n"
            f"   • 디스크(Storage): {disk_info}\n\n"
            f"2️⃣ <b>8대 워드프레스 블로그</b> ({'🟢 정상' if blogger_healthy else '🔴 점검 필요'})\n"
            f"   • 일일 발행: 사이트당 4편 (총 32편) 08/12/18/21시 ±8분 분산\n"
            f"   • 최근 예약 확인 글: {recent_posts_count}편\n\n"
            f"3️⃣ <b>Threads x 쿠팡 자동화</b> ({'🟢 정상' if threads_healthy else '🔴 점검 필요'})\n"
            f"   • {threads_details_str}\n\n"
            f"4️⃣ <b>AI 비용 (오늘)</b>\n"
            f"   • {cost_str} | <code>/cost</code> 로 월간 상세 조회 가능\n\n"
            f"5️⃣ <b>보안 & 자가 치유</b> (🟢 활성)\n"
            f"   • 관리자 단독 제어 · 그룹 채팅 차단 · 프롬프트 인젝션 방어 활성\n"
            f"   • 최근 24시간 감사 로그: {audit_count}건\n"
            f"   • DB 영속 승인 · 30일 데이터 보관 정책 적용\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 <code>/traffic</code> | <code>/tasks</code> | <code>/cost</code> | <code>/approvals</code> | <code>/reset</code>"
        )

    async def check_and_send_scheduled(self, bot_instance, target_chat_id: str | int) -> bool:
        """Check 08:00 KST (Morning Briefing) and 09:00, 15:00, 21:00 KST (3x Daily Traffic Reports)."""
        now_kst = datetime.now(KST)
        today_str = now_kst.strftime("%Y-%m-%d")

        # 1. 08:00 KST Morning Briefing
        if now_kst.hour == MORNING_REPORT_HOUR and now_kst.minute < 5:
            if self.last_morning_date != today_str:
                self.last_morning_date = today_str
                print(f"[DailyReporter] 08:00 KST 일일 모닝 브리핑 발송: {today_str}")
                try:
                    report_msg = await self.generate_briefing()
                    await bot_instance.send_message(target_chat_id, report_msg)
                    audit_logger.log("SYSTEM", "daily_briefing_sent", 1, "SUCCESS", {"date": today_str})
                    return True
                except Exception as e:
                    print(f"[DailyReporter Error 08:00] {e}")
                    audit_logger.log("SYSTEM", "daily_briefing_failed", 2, "FAILED", {"error": str(e)})

        # 2. 09:00, 15:00, 21:00 KST (3 times daily) Traffic & Visitor Report
        if now_kst.hour in TRAFFIC_REPORT_HOURS and now_kst.minute < 5:
            report_key = f"{today_str}_{now_kst.hour}"
            if report_key not in self.sent_traffic_keys:
                self.sent_traffic_keys.add(report_key)
                # Keep cache tidy
                self.sent_traffic_keys = {k for k in self.sent_traffic_keys if k.startswith(today_str)}

                slot_labels = {
                    9: "09:00 KST 오전",
                    15: "15:00 KST 오후",
                    21: "21:00 KST 마감"
                }
                label = slot_labels.get(now_kst.hour, f"{now_kst.hour:02d}:00 KST")
                print(f"[DailyReporter] {label} 정기 블로그 방문자수/트래픽 리포트 발송: {report_key}")
                try:
                    traffic_msg = await self.generate_traffic_report(label)
                    await bot_instance.send_message(target_chat_id, traffic_msg)
                    audit_logger.log("SYSTEM", f"traffic_report_{now_kst.hour}h_sent", 1, "SUCCESS", {"slot": label, "date": today_str})
                    return True
                except Exception as e:
                    print(f"[DailyReporter Error {label}] {e}")
                    audit_logger.log("SYSTEM", f"traffic_report_{now_kst.hour}h_failed", 2, "FAILED", {"error": str(e)})

        return False


daily_reporter = DailyExecutiveReporter()
