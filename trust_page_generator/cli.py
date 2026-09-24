"""Command Line Interface for Trust Page Generator V1.0.
Provides operator commands to generate, inspect, preview, and deploy trust pages.
Adheres strictly to Rule 3 (Windows UTF-8 Encoding Safety).
"""
import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Rule 3: Enforce Windows UTF-8 stdout/stderr reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from trust_page_generator.config import BLOG_REGISTRY
from trust_page_generator.database.session import init_db, SessionLocal
from trust_page_generator.database.models import BlogIdentity, TrustPage
from trust_page_generator.identities import MASTER_IDENTITIES, sync_identities_to_db
from trust_page_generator.generator import TrustPageGenerator
from trust_page_generator.publisher import WordPressTrustPagePublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("trust_page_generator.cli")


def cmd_generate() -> None:
    """Generate all identities and 8 trust pages for each blog."""
    init_db()
    gen = TrustPageGenerator()
    print("\n" + "=" * 60)
    print("🚀 8대 WordPress 블로그 Brand Identity 및 Trust Page 생성 시작...")
    print("=" * 60)

    count = gen.build_and_save_all_to_db()
    print(f"✅ 생성 완료! 총 {count}개 페이지가 DB(trust_pages.db)에 준비되었습니다.\n")


def cmd_status() -> None:
    """Display status of all 8 blogs and their trust pages."""
    init_db()
    db = SessionLocal()
    try:
        identities = db.query(BlogIdentity).all()
        pages = db.query(TrustPage).all()

        print("\n" + "=" * 65)
        print("🏛️ WordPress Multi-Blog Trust Page Generator V1.0 현황")
        print("=" * 65)
        print(f"• 등록된 블로그 수: {len(identities)}개")
        print(f"• 생성된 신뢰 페이지 수: 총 {len(pages)}개 (블로그당 8개)")
        print("-" * 65)

        for ident in identities:
            b_pages = [p for p in pages if p.blog_id == ident.blog_id]
            pub_cnt = sum(1 for p in b_pages if p.status == "PUBLISHED")
            print(f"[{ident.blog_id}] {ident.brand_name} ({ident.domain})")
            print(f"    카테고리: {ident.category}")
            print(f"    톤 & 매너: {ident.tone}")
            print(f"    신뢰 메시지: {ident.trust_message[:60]}...")
            print(f"    페이지 준비 현황: {len(b_pages)}개 생성 완료 (배포됨: {pub_cnt}개)")
            for p in b_pages:
                print(f"      - /{p.slug} : {p.title[:30]}... [{p.status}]")
            print()
        print("=" * 65 + "\n")
    finally:
        db.close()


def cmd_preview(blog_id: int, page_slug: str) -> None:
    """Print the HTML preview of a specific page."""
    init_db()
    db = SessionLocal()
    try:
        page = db.query(TrustPage).filter(
            TrustPage.blog_id == blog_id,
            TrustPage.slug == page_slug
        ).first()

        if not page:
            print(f"❌ 해당 페이지를 찾을 수 없습니다. (Blog ID: {blog_id}, Slug: {page_slug})")
            return

        print("\n" + "=" * 60)
        print(f"📄 미리보기: [{page.blog_id}] {page.title} (/{page.slug})")
        print("=" * 60)
        print(page.content[:1500])
        print("\n... (이하 생략 - 전체 " + str(len(page.content)) + " 바이트) ...\n")
    finally:
        db.close()


async def cmd_deploy(dry_run: bool = False, blog_id: int = None) -> None:
    """Deploy pages to WordPress via REST API."""
    init_db()
    targets = [blog_id] if blog_id else list(BLOG_REGISTRY.keys())
    print("\n" + "=" * 60)
    print(f"🌐 WordPress Trust Page 배포 시작 (dry_run={dry_run}, 대상: {len(targets)}개 블로그)...")
    print("=" * 60)

    for b_id in targets:
        cfg = BLOG_REGISTRY.get(b_id)
        if not cfg:
            continue
        pub = WordPressTrustPagePublisher(cfg)
        res = await pub.deploy_all_for_blog(dry_run=dry_run)
        print(f"• [{cfg['name']}] 배포 결과: 성공 {res['success_count']}건 / 실패 {res['failed_count']}건")
        for d in res["details"]:
            if "url" in d:
                print(f"   ✓ /{d['slug']} -> {d['url']}")
            elif "error" in d:
                print(f"   ✗ /{d['slug']} -> 에러: {d['error']}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Trust Page Generator CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("generate", help="Generate all Brand Identities and Trust Pages into DB")
    subparsers.add_parser("status", help="Show system and page generation status")

    prev_parser = subparsers.add_parser("preview", help="Preview generated page HTML")
    prev_parser.add_argument("--blog", type=int, required=True, help="Blog ID (1~8)")
    prev_parser.add_argument("--page", type=str, required=True, help="Page slug (e.g. about-us, terms)")

    deploy_parser = subparsers.add_parser("deploy", help="Deploy pages to WordPress via REST API")
    deploy_parser.add_argument("--dry-run", action="store_true", help="Simulate without creating actual pages")
    deploy_parser.add_argument("--blog", type=int, default=None, help="Target specific Blog ID (default: all)")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate()
    elif args.command == "status":
        cmd_status()
    elif args.command == "preview":
        cmd_preview(args.blog, args.page)
    elif args.command == "deploy":
        asyncio.run(cmd_deploy(dry_run=args.dry_run, blog_id=args.blog))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
