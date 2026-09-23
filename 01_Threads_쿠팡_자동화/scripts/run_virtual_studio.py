import os
import sys
import argparse

sys.path.insert(0, os.path.abspath('.'))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database.connection import SessionLocal
from services.virtual_studio_service import VirtualStudioService

def main():
    parser = argparse.ArgumentParser(description="가상의 직원 3명 스튜디오 (Virtual Studio 3-Agent Runner)")
    parser.add_argument("--product_id", type=int, default=11, help="Target product ID (default: 11)")
    parser.add_argument("--type", type=str, default="both", choices=["toon", "cardnews", "both"], help="Content type")
    parser.add_argument("--img", type=str, default=None, help="Custom image path")
    args = parser.parse_args()

    print("=" * 60)
    print("🚀 [가상의 직원 3명 스튜디오] 업무 파이프라인 가동")
    print(f"• 타겟 상품 ID: {args.product_id}")
    print(f"• 제작 포맷: {args.type}")
    print("=" * 60)

    db = SessionLocal()
    try:
        studio = VirtualStudioService(db)
        
        print("\n[1단계: 직원 1 - trend_curator] 상품 및 바이럴 팩트 큐레이션 중...")
        curated = studio.run_curator(args.product_id)
        print(f"  ✓ 상품명: {curated['name']}")
        print(f"  ✓ 카테고리: {curated['category']} | 출처: {curated['source']}")

        print("\n[2단계: 직원 2 - story_writer] E-E-A-T 기반 인스타툰/카드뉴스 스토리보드 작성 중...")
        results = studio.produce(args.product_id, content_type=args.type, custom_img_path=args.img)

        print("\n[3단계: 직원 3 - visual_designer] 1080x1350 초고화질 PNG 렌더링 완료!")
        for ctype, path in results.items():
            print(f"  ✓ [{ctype}] 생성 완료: {path}")

    finally:
        db.close()

    print("\n" + "=" * 60)
    print("✨ 모든 제작 및 출고가 100% 자율 완료되었습니다!")
    print("=" * 60)

if __name__ == '__main__':
    main()
