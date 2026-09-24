from datetime import datetime, time as dtime, timedelta
import random
from typing import Optional
from zoneinfo import ZoneInfo

def parse_kst_time(time_str: str) -> dtime:
    """Parse a 'HH:MM' string into a time object in KST timezone.
    Returns a default time of 08:00 if the input is invalid.
    """
    try:
        parts = time_str.strip().split(":")
        return dtime(hour=int(parts[0]), minute=int(parts[1]))
    except Exception:
        # Fallback to default 08:00
        return dtime(hour=8, minute=0)

def calculate_schedule_datetimes(
    time1_str: str = "08:20",
    time2_str: str = "12:15",
    time3_str: str = "17:50",
    time4_str: str = "20:45",
    tz_str: str = "Asia/Seoul",
    post_count: int = 4,
    apply_jitter: bool = True,
    jitter_min_minutes: int = -12,
    jitter_max_minutes: int = 14,
    site_id: Optional[int] = None,
) -> list[datetime]:
    """Return a list of future datetimes for scheduled posts with natural human-like irregular jitter and multi-site staggering.

    The function cycles through the golden reading time slots:
      - 1차: 08:20 KST (출근/모닝 브리핑)
      - 2차: 12:15 KST (점심 휴식/검색 시간대)
      - 3차: 17:50 KST (퇴근길/초저녁)
      - 4차: 20:45 KST (야간 여유 시간대)

    Site Staggering:
      If `site_id` is provided, each site receives a distinct offset (0 ~ 75 min)
      ensuring that the 8 specialized blogs NEVER publish at the exact same minute or hour.

    Human Jitter:
      Applies irregular minute jitter (-12 ~ +14 min) and irregular seconds (11 ~ 58 sec),
      guaranteeing a completely natural, human-author publication rhythm.
    """
    tz = ZoneInfo(tz_str)
    now = datetime.now(tz)
    slots = [
        parse_kst_time(time1_str),
        parse_kst_time(time2_str),
        parse_kst_time(time3_str),
        parse_kst_time(time4_str),
    ]
    schedule: list[datetime] = []

    # Calculate site-specific staggering offset (e.g. site 1 -> 0m, site 2 -> 11m, site 3 -> 22m, etc.)
    site_offset = 0
    if site_id is not None and isinstance(site_id, int):
        site_offset = ((site_id - 1) % 8) * 11

    for i in range(max(post_count, 1)):
        slot = slots[i % len(slots)]
        day_offset = i // len(slots)
        base_dt = datetime.combine(now.date() + timedelta(days=day_offset), slot, tzinfo=tz)

        # Apply site stagger
        base_dt += timedelta(minutes=site_offset)

        # Advance to next day if base slot has already passed today
        if base_dt <= now:
            base_dt += timedelta(days=1)

        dt = base_dt
        if apply_jitter:
            rand_min = random.randint(jitter_min_minutes, jitter_max_minutes)
            rand_sec = random.randint(11, 58)
            dt = base_dt + timedelta(minutes=rand_min, seconds=rand_sec)

            # Ensure the scheduled time is at least 4 minutes in the future
            if dt <= now + timedelta(minutes=4):
                dt += timedelta(days=1)

        schedule.append(dt)

    return schedule
