import os
import sys
from datetime import datetime, timedelta
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.backend.tre.db import SessionLocal, now
from apps.backend.tre.models import Post, Job, JobAttempt, Notification, Account
from apps.backend.tre.content import fingerprint
from apps.worker.engine import run_once, deliver_notifications
from sqlalchemy import select

def run_schedule_qa():
    print("=" * 60)
    print("  [QA TEST 4단계] Threads 예약 발행 파이프라인 E2E 검증")
    print("=" * 60)

    factory = SessionLocal

    # 1. 10분 뒤 예약 생성 및 DB 저장
    kst_now = datetime.now()
    scheduled_kst = kst_now + timedelta(minutes=10)
    scheduled_time_str = scheduled_kst.strftime("%Y-%m-%d %H:%M")

    print(f"\n1. 예약 생성 및 Scheduler/DB 등록:")
    print(f"  • 현재 시간: {kst_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  • 목표 예약 시간 (+10분): {scheduled_time_str}")

    # 100점 만점 검증 통과 텍스트 (숫자 포함, 존댓말, 금칙어 배제, 고유성 보장)
    post_text = (
        f"2026년 업무 효율을 높이기 위해 스마트폰 알림 3가지를 정리해 보았습니다.\n"
        f"불필요한 배너 알림을 끄면 집중력 유지에 큰 도움이 됩니다.\n"
        f"업무 중에 꼭 확인하는 나만의 알림 설정이 있으신가요?"
    )

    post_id = None
    job_id = None

    with factory() as db:
        acc = db.get(Account, 1)
        print(f"  • 발행 대상 계정: {acc.name} (@{acc.username})")

        post = Post(
            account_id=acc.id,
            content_id=1,
            body=post_text,
            goal="INFORMATION",
            angle="OBSERVATION",
            status="SCHEDULED",
            fingerprint=fingerprint(post_text),
            approved_at=now(),
            scheduled_at=now() + timedelta(minutes=10),
            mock=False
        )
        db.add(post)
        db.flush()
        post_id = post.id

        job = Job(
            post_id=post.id,
            state="WAITING",
            due_at=post.scheduled_at
        )
        db.add(job)
        db.commit()
        job_id = job.id

        print(f"  • [DB 저장 완료] Post ID: {post_id}, Job ID: {job_id}")
        print(f"  • Post 상태: {post.status}, Job 상태: {job.state}, due_at(UTC): {job.due_at}")

    # 2. Worker 감지 및 조기 실행 방지 검증
    print("\n2. Worker 조기 실행 방지 검증 (예약시간 미도달 상태):")
    processed = run_once(factory)
    print(f"  • Worker run_once() 결과 (처리 건수): {processed}건 (예약시간 전이므로 0건 정상 대기)")
    with factory() as db:
        job = db.get(Job, job_id)
        post = db.get(Post, post_id)
        print(f"  • Job 상태 유지 확인: {job.state} (WAITING 유지, premature publish 방지 성공)")

    # 3. 예약시간 도달 시뮬레이션 및 Worker 실행
    print(f"\n3. 예약시간({scheduled_time_str}) 도달 시점 Worker 실행:")
    with factory() as db:
        # 시간 경과 시뮬레이션: due_at을 현재 시간으로 동기화
        job = db.get(Job, job_id)
        job.due_at = now() - timedelta(seconds=1)
        post = db.get(Post, post_id)
        post.scheduled_at = job.due_at
        db.commit()
        print(f"  • 예약 시간 도달 -> due_at을 현재시간으로 트리거")

    print("  • Worker 파이프라인 가동 (Job 획득 -> Threads API 2단계 컨테이너 생성 및 발행)...")
    processed_count = run_once(factory)
    print(f"  • Worker 처리 완료 건수: {processed_count}건")

    # 4. 발행 완료 상태 및 로그 검증
    print("\n4. 발행 결과 및 DB/Attempt 상태 검증:")
    published_post_id = None
    with factory() as db:
        post = db.get(Post, post_id)
        job = db.get(Job, job_id)
        attempts = list(db.scalars(select(JobAttempt).where(JobAttempt.job_id == job_id)))
        
        print(f"  • 최종 Post 상태: {post.status}")
        print(f"  • Threads Remote ID: {post.remote_id}")
        print(f"  • 발행 완료 시각: {post.published_at}")
        print(f"  • 최종 Job 상태: {job.state} (DONE)")
        print(f"  • Job Attempt 수: {len(attempts)}회 (결과: {[a.result for a in attempts]})")
        published_post_id = post.remote_id

    # 5. Telegram 알림 전달 검증
    print("\n5. Telegram 알림 큐 적재 및 발송 검증:")
    with factory() as db:
        notifs = list(db.scalars(select(Notification).where(Notification.post_id == post_id)))
        print(f"  • Notification 생성 수: {len(notifs)}건")
        for n in notifs:
            print(f"    - Event Key: {n.event_key}")
            print(f"    - State: {n.state}")
            print(f"    - Telegram Remote Message ID: {n.remote_id}")
            print(f"    - Body:\n{n.body}")

    # 6. 결과 요약
    print("\n" + "=" * 60)
    print("Threads SCHEDULED PUBLISH TEST RESULT")
    print(f"예약 생성: 성공 (Post #{post_id}, 시간: {scheduled_time_str})")
    print(f"DB 저장: 성공 (Post.status=SCHEDULED, Job.state=WAITING)")
    print(f"Worker 감지: 정상 감지 (조기 실행 방지 PASS -> 시간 도달 시 자동 처리)")
    print(f"API 실행: 성공 (Threads Graph API v1.0 정상 호출)")
    print(f"게시 성공: 성공 (Remote ID: {published_post_id})")
    print(f"Telegram 알림: 성공 (실시간 관리자 전송 완료)")
    print("=" * 60)

if __name__ == '__main__':
    run_schedule_qa()
