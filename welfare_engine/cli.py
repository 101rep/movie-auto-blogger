"""Command Line Interface for Welfare Content Auto Publishing Engine V1.0.
Provides operator controls, manual triggers, status queries, and test utilities.
Adheres strictly to Rule 3 (Windows UTF-8 Encoding Safety).
"""
import argparse
import asyncio
import logging
import sys
from datetime import date
from pathlib import Path

# Rule 3: Enforce Windows UTF-8 stdout/stderr reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from welfare_engine.config import settings, WELFARE_BLOGS, BLOG_A, BLOG_B, BLOG_C
from welfare_engine.database.session import init_db, SessionLocal
from welfare_engine.database.models import WelfareContent, WelfarePublication, ContentStatus
from welfare_engine.agent.collector import WelfareDataCollector
from welfare_engine.agent.evaluator import WelfareEvaluator
from welfare_engine.agent.image_generator import WelfareCardNewsGenerator
from welfare_engine.reporter.telegram_reporter import WelfareTelegramReporter
from welfare_engine.worker.pipeline import WelfarePipelineController

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("welfare_engine.cli")


def cmd_status() -> None:
    """Print current database and publication statistics."""
    init_db()
    db = SessionLocal()
    try:
        total_contents = db.query(WelfareContent).count()
        new_cnt = db.query(WelfareContent).filter(WelfareContent.status == ContentStatus.NEW.value).count()
        ready_cnt = db.query(WelfareContent).filter(WelfareContent.status == ContentStatus.READY.value).count()
        published_cnt = db.query(WelfareContent).filter(WelfareContent.status == ContentStatus.PUBLISHED.value).count()
        hold_cnt = db.query(WelfareContent).filter(WelfareContent.status == ContentStatus.HOLD.value).count()

        total_pubs = db.query(WelfarePublication).count()
        verified_pubs = db.query(WelfarePublication).filter(WelfarePublication.verification_status == "VERIFIED").count()
        failed_pubs = db.query(WelfarePublication).filter(WelfarePublication.verification_status == "FAILED").count()

        print("\n" + "=" * 50)
        print("🏛️ Welfare Content Auto Publishing Engine V1.0 현황")
        print("=" * 50)
        print(f"• 전체 수집 정책 수: {total_contents}건")
        print(f"  - 신규(NEW): {new_cnt}건")
        print(f"  - 준비완료(READY): {ready_cnt}건")
        print(f"  - 발행완료(PUBLISHED): {published_cnt}건")
        print(f"  - 보류(HOLD): {hold_cnt}건")
        print("-" * 50)
        print(f"• 워드프레스 발행 내역: 총 {total_pubs}건")
        print(f"  - 검증 성공(VERIFIED): {verified_pubs}건")
        print(f"  - 검증 실패(FAILED): {failed_pubs}건")
        print("-" * 50)
        print("• 3대 복지 블로그 매핑:")
        for k, b in WELFARE_BLOGS.items():
            cnt = db.query(WelfarePublication).filter(WelfarePublication.blog_key == k).count()
            print(f"  [{k}] {b.name} ({b.domain}) | 페르소나: {b.persona_name} | 발행: {cnt}건")
        print("=" * 50 + "\n")
    finally:
        db.close()


async def cmd_collect() -> None:
    """Collect policies from OpenAPI and RSS."""
    init_db()
    collector = WelfareDataCollector()
    print("정부24, 공공데이터포털, RSS 정책 수집 시작...")
    items = await collector.collect_all(limit=25)
    saved = collector.save_to_database(items)
    print(f"수집 완료: 총 {len(items)}건 수집, 신규 {len(saved)}건 DB 저장 완료.")

    # Trigger evaluation
    evaluator = WelfareEvaluator()
    db = SessionLocal()
    try:
        unevaluated = db.query(WelfareContent).filter(WelfareContent.status == ContentStatus.NEW.value).all()
        for c in unevaluated:
            evaluator.evaluate_and_update(c)
        db.commit()
        print(f"소재 평가 완료: {len(unevaluated)}건 100점 만점 평가 완료.")
    finally:
        db.close()


async def cmd_run(dry_run: bool = False, days: int = 1) -> None:
    """Run publishing pipeline."""
    init_db()
    controller = WelfarePipelineController()
    print(f"Welfare Engine 파이프라인 실행 (Day {days}, dry_run={dry_run})...")
    res = await controller.run_pipeline(
        target_date=date.today(),
        days_since_launch=days,
        dry_run=dry_run
    )
    print("파이프라인 실행 결과:", res)


async def cmd_test_telegram() -> None:
    """Test Telegram connection and report format."""
    reporter = WelfareTelegramReporter()
    sample_stats = {
        "BLOG_A": {"scheduled": 3, "success": 3},
        "BLOG_B": {"scheduled": 3, "success": 3},
        "BLOG_C": {"scheduled": 3, "success": 3}
    }
    sample_errors = []
    print("텔레그램 운영 리포트 테스트 발송 중...")
    success = await reporter.send_daily_report(sample_stats, sample_errors)
    print("텔레그램 발송 결과:", "성공" if success else "실패")


def cmd_test_image() -> None:
    """Test generating a card news thumbnail."""
    init_db()
    db = SessionLocal()
    try:
        content = db.query(WelfareContent).first()
        if not content:
            content = WelfareContent(
                id=999,
                title="2026 청년월세 한시 특별지원 (최대 월 20만원 지원)",
                category="청년지원",
                target="만 19~34세 무주택 청년",
                age="만 19~34세",
                amount="월 최대 20만원 (12회 지원)",
                deadline="2026-12-31"
            )
        gen = WelfareCardNewsGenerator()
        path = gen.generate_card_news(content, BLOG_A)
        print(f"카드뉴스 생성 성공: {path} (존재: {path.exists()})")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Welfare Engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Show system status")
    subparsers.add_parser("collect", help="Run data collection and evaluation")

    run_parser = subparsers.add_parser("run", help="Run full publishing pipeline")
    run_parser.add_argument("--dry-run", action="store_true", help="Simulate without WordPress publishing")
    run_parser.add_argument("--days", type=int, default=1, help="Days since launch (default: 1)")

    subparsers.add_parser("test-telegram", help="Send test report via Telegram")
    subparsers.add_parser("test-image", help="Generate test card news image")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "collect":
        asyncio.run(cmd_collect())
    elif args.command == "run":
        asyncio.run(cmd_run(dry_run=args.dry_run, days=args.days))
    elif args.command == "test-telegram":
        asyncio.run(cmd_test_telegram())
    elif args.command == "test-image":
        cmd_test_image()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
