import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import Account, Product, PickProfile, PickItem
from database.repository import Repository

logger = logging.getLogger("PickSourcer")

# 4대 커머스 플랫폼별 검증된 실시간 인기 핫딜 카탈로그 데이터베이스
CURATED_PLATFORM_CATALOG = {
    # 🏢 버티컬 - IT / 테크 (@kth.101rep)
    "IT_TECH": [
        {
            "title": "벨킨 3in1 맥세이프 고속 무선 충전 거치대",
            "subtitle": "맥북/아이폰/애플워치 한방에 거치, 데스크테리어 종결템",
            "curator_comment": "내돈내산 2년째 잔고장 0개. 책상 위 케이블 3개 지옥에서 벗어나게 해 준 인생템입니다.",
            "affiliate_platform": "COUPANG",
            "original_price": 179000,
            "sale_price": 129000,
            "discount_rate": 28,
            "badge_text": "🚀 로켓배송",
            "image_url": "https://images.unsplash.com/photo-1586105251261-72a756497a11?w=600&auto=format&fit=crop",
            "affiliate_url": "https://link.coupang.com/a/bM_kth101rep_belkin",
            "is_pinned": True
        },
        {
            "title": "베이스어스 65W GaN 질화갈륨 초소형 3포트 고속 충전기",
            "subtitle": "벽돌 충전기 버리세요. 손바닥 절반 크기에 맥북 프로까지 풀충전",
            "curator_comment": "카페나 출장 갈 때 이거 하나만 챙기면 노트북, 폰, 태블릿 동시 충전 끝.",
            "affiliate_platform": "ALIEXPRESS",
            "original_price": 38000,
            "sale_price": 18900,
            "discount_rate": 50,
            "badge_text": "⚡ 50% 특가",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop",
            "affiliate_url": "https://s.click.aliexpress.com/e/_dBaseus65W_kth",
            "is_pinned": False
        },
        {
            "title": "로지텍 MX Master 3S 무소음 무선 블루투스 마우스",
            "subtitle": "개발자/디자이너 손목터널증후군 퇴치 필수 마우스",
            "curator_comment": "초고속 휠 스크롤 한 번 써보면 일반 마우스로는 절대 못 돌아갑니다.",
            "affiliate_platform": "COUPANG",
            "original_price": 139000,
            "sale_price": 119000,
            "discount_rate": 14,
            "badge_text": "🔥 베스트셀러",
            "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop",
            "affiliate_url": "https://link.coupang.com/a/bM_mxmaster3s_kth",
            "is_pinned": False
        },
        {
            "title": "알루미늄 접이식 360도 회전 노트북 맥북 거치대",
            "subtitle": "목 디스크 예방! 눈높이 맞춤 조절 및 흔들림 없는 메탈 프레임",
            "curator_comment": "타건할 때 덜덜 떨리지 않고 짱짱해서 작업 효율이 2배 올라갑니다.",
            "affiliate_platform": "OHOUSE",
            "original_price": 42000,
            "sale_price": 28900,
            "discount_rate": 31,
            "badge_text": "🏠 오늘의집 PICK",
            "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop",
            "affiliate_url": "https://ohou.se/curator/links/kth_stand",
            "is_pinned": False
        },
        {
            "title": "앤커 67W 3포트 초고속 충전기 & 100W 실리콘 케이블 세트",
            "subtitle": "토스 10% 단독 공구! 맥북+아이폰 동시 초고속 충전 완벽 지원",
            "curator_comment": "토스 쉐어링크 10% 추가할인 특가로 풀렸습니다. 발열 없고 컴팩트해서 출퇴근 가방 필수품!",
            "affiliate_platform": "TOSS",
            "original_price": 54000,
            "sale_price": 36900,
            "discount_rate": 32,
            "badge_text": "⚡ 토스 10% 특가",
            "image_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop",
            "affiliate_url": "https://toss.im/_m/share?id=anker_67w_kth",
            "is_pinned": False
        }
    ],

    # 🏢 버티컬 - 뷰티 / 패션 / 자기관리 (@lookatmeai)
    "BEAUTY": [
        {
            "title": "라운드랩 1025 독도 토너 500ml 대용량 + 200ml 증정 기획",
            "subtitle": "화해 3년 연속 1위! 속건조 잡아주는 국민 진정 토너",
            "curator_comment": "올영 세일 때 안 사면 100% 후회하는 꿀템. 7스킨법으로 화장 안 뜨게 해줍니다.",
            "affiliate_platform": "OLIVE_YOUNG",
            "original_price": 45000,
            "sale_price": 27900,
            "discount_rate": 38,
            "badge_text": "✨ 올영 단독기획",
            "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop",
            "affiliate_url": "https://affiliate.oliveyoung.co.kr/dokdo_lookatme",
            "is_pinned": True
        },
        {
            "title": "넘버즈인 5번 글루타치온C 흔적 패드 70매",
            "subtitle": "잡티/색소침착 2주 집중 케어, 올리브영 랭킹 1위 패드",
            "curator_comment": "아침 메이크업 전 볼에 3분 얹어두면 안색이 맑아지고 피부결 정돈 끝!",
            "affiliate_platform": "OLIVE_YOUNG",
            "original_price": 28000,
            "sale_price": 19600,
            "discount_rate": 30,
            "badge_text": "🔥 랭킹 1위",
            "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop",
            "affiliate_url": "https://affiliate.oliveyoung.co.kr/numbuzin5_lookatme",
            "is_pinned": False
        },
        {
            "title": "헤드스파7 파란눈 트리트먼트 대용량 300ml 듀오",
            "subtitle": "손상모 7초 물미역 케어! 탈모 증상 완화 기능성",
            "curator_comment": "염색 자주 해서 빗질 안 되던 머릿결이 물미역처럼 부드러워져요.",
            "affiliate_platform": "COUPANG",
            "original_price": 54000,
            "sale_price": 29800,
            "discount_rate": 45,
            "badge_text": "🚀 로켓와우",
            "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&auto=format&fit=crop",
            "affiliate_url": "https://link.coupang.com/a/bM_headspa7_lookatme",
            "is_pinned": False
        },
        {
            "title": "아누아 어성초 77 진정 토너 350ml 대용량 기획 세트",
            "subtitle": "토스 단독 10% 공구! 붉은기 진정 여드름 피부 국민 진정 토너",
            "curator_comment": "토스페이 결제 시 10% 추가 혜택 적용되는 숨은 공구 좌표예요. 환절기 좁쌀여드름 순삭!",
            "affiliate_platform": "TOSS",
            "original_price": 38000,
            "sale_price": 23500,
            "discount_rate": 38,
            "badge_text": "⚡ 토스 10% 공구",
            "image_url": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=600&auto=format&fit=crop",
            "affiliate_url": "https://toss.im/_m/share?id=anua77_lookatme",
            "is_pinned": False
        }
    ],

    # 🏢 버티컬 - 살림로그 / 리빙 / 주방 (@yr170425)
    "LIVING": [
        {
            "title": "실리팟 100% 플래티넘 실리콘 밀폐용기 4종 세트",
            "subtitle": "전자레인지/식세기/열탕소독 가능! 변색 냄새배임 없는 살림템",
            "curator_comment": "플라스틱 반찬통 싹 버리고 정착했어요. 냉동밥 데워도 유해물질 걱정 제로!",
            "affiliate_platform": "OHOUSE",
            "original_price": 68000,
            "sale_price": 42900,
            "discount_rate": 37,
            "badge_text": "🏠 오늘의집 베스트",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop",
            "affiliate_url": "https://ohou.se/curator/links/yr_silicone",
            "is_pinned": True
        },
        {
            "title": "스탠리 퀜처 H2.0 플로우스테이트 텀블러 887ml",
            "subtitle": "얼음이 40시간 유지되는 보냉력 끝판왕 손잡이 텀블러",
            "curator_comment": "운전할 때 컵홀더에 쏙 들어가고, 하루 물 2L 채우기 정말 쉬워집니다.",
            "affiliate_platform": "COUPANG",
            "original_price": 53000,
            "sale_price": 45000,
            "discount_rate": 15,
            "badge_text": "🚀 로켓배송",
            "image_url": "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=600&auto=format&fit=crop",
            "affiliate_url": "https://link.coupang.com/a/bM_stanley_yr",
            "is_pinned": False
        },
        {
            "title": "스마트 모션센서 무소음 슬림 쓰레기통 12L",
            "subtitle": "손 대지 않아도 스르륵! 냄새 완벽 차단 밀폐 휴지통",
            "curator_comment": "주방 싱크대 옆이랑 화장실에 필수. 기저귀나 음식물 냄새 싹 잡아줍니다.",
            "affiliate_platform": "OHOUSE",
            "original_price": 39000,
            "sale_price": 24900,
            "discount_rate": 36,
            "badge_text": "✨ 살림꿀팁",
            "image_url": "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=600&auto=format&fit=crop",
            "affiliate_url": "https://ohou.se/curator/links/yr_smartbin",
            "is_pinned": False
        },
        {
            "title": "바겐슈타이거 올스텐 304 분리형 주방가위 & 채칼 세트",
            "subtitle": "토스 단독 10% 특가! 녹슬지 않고 식세기 열탕소독 가능한 위생 가위",
            "curator_comment": "생닭 뼈까지 숭덩 잘리는 절삭력! 토스 공구로 마트보다 만원 이상 저렴하게 떴습니다.",
            "affiliate_platform": "TOSS",
            "original_price": 35000,
            "sale_price": 19800,
            "discount_rate": 43,
            "badge_text": "⚡ 토스 10% 특가",
            "image_url": "https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=600&auto=format&fit=crop",
            "affiliate_url": "https://toss.im/_m/share?id=vagen_scissors_yr",
            "is_pinned": False
        }
    ],

    # 🔥 트렌드 - 툰툰이 꿀템 / 캐릭터 / 데스크테리어 (@toontoooon)
    "TREND_TOON": [
        {
            "title": "우주비행사 오로라 은하수 빔프로젝터 무드등",
            "subtitle": "방 전체가 오로라 우주로 변신! 리모컨 각도조절 취침등",
            "curator_comment": "불 끄고 켜는 순간 감성 미쳤습니다.. 침대에 누워서 멍때리기 최고봉!",
            "affiliate_platform": "ALIEXPRESS",
            "original_price": 35000,
            "sale_price": 14200,
            "discount_rate": 59,
            "badge_text": "🎉 바이럴 대란템",
            "image_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop",
            "affiliate_url": "https://s.click.aliexpress.com/e/_dToonAstronaut",
            "is_pinned": True
        },
        {
            "title": "미드센추리 모던 버섯 무선 터치 단스탠드 조명",
            "subtitle": "책상/침실 무드 완성! 3색 변환 충전식 무선 조명",
            "curator_comment": "선 없이 어디든 들고 다닐 수 있어서 데스크 사진 찍을 때 치트키예요.",
            "affiliate_platform": "OHOUSE",
            "original_price": 32000,
            "sale_price": 19800,
            "discount_rate": 38,
            "badge_text": "🏠 데스크테리어",
            "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop",
            "affiliate_url": "https://ohou.se/curator/links/toon_lamp",
            "is_pinned": False
        },
        {
            "title": "미니 고양이 발바닥 책상 온열 핸드워머 마우스패드",
            "subtitle": "수족냉증 직장인/학생 구원템! 따끈따끈 온도 조절",
            "curator_comment": "겨울에 손 시려서 마우스 못 잡는 분들 필수템. 귀여움 한도초과!",
            "affiliate_platform": "COUPANG",
            "original_price": 25000,
            "sale_price": 16500,
            "discount_rate": 34,
            "badge_text": "🚀 로켓배송",
            "image_url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600&auto=format&fit=crop",
            "affiliate_url": "https://link.coupang.com/a/bM_catpad_toon",
            "is_pinned": False
        },
        {
            "title": "레트로 픽셀 아트 블루투스 스피커 디붐 디투 플러스",
            "subtitle": "토스 10% 한정 공구! 책상 위 픽셀 애니메이션 + 고음질 사운드",
            "curator_comment": "데스크테리어 끝판왕. 토스 쉐어링크 24시간 특별가로 풀렸을 때 무조건 쟁여두세요!",
            "affiliate_platform": "TOSS",
            "original_price": 129000,
            "sale_price": 89000,
            "discount_rate": 31,
            "badge_text": "⚡ 토스 10% 한정",
            "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop",
            "affiliate_url": "https://toss.im/_m/share?id=divoom_ditoo_toon",
            "is_pinned": False
        }
    ],

    # 🔥 트렌드 - 호구탈출 가성비 비교 / 핫딜 (@101rep80)
    "HOT_DEAL": [
        {
            "title": "투키(Toocki) C to C 100W 실시간 출력표시 디스플레이 케이블",
            "subtitle": "충전 속도 W수가 눈으로 보임! 국내 1.5만원짜리 알리 1천원대",
            "curator_comment": "호구 탈출 1호 꿀템. 쿠팡에 만원 넘게 파는 거랑 완전 똑같은 제품입니다.",
            "affiliate_platform": "ALIEXPRESS",
            "original_price": 15000,
            "sale_price": 2100,
            "discount_rate": 86,
            "badge_text": "🔥 86% 폭풍할인",
            "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=600&auto=format&fit=crop",
            "affiliate_url": "https://s.click.aliexpress.com/e/_dToocki100W_101rep",
            "is_pinned": True
        },
        {
            "title": "해피콜 플렉스팬 IH 와이드 22cm 만능 멀티팬",
            "subtitle": "냄비+프라이팬+웍 하나로 끝! 자취생/신혼 필수 가성비 팬",
            "curator_comment": "라면 끓이고 볶음밥하고 파스타까지 이거 하나로 다 됩니다. 코팅력 최상!",
            "affiliate_platform": "COUPANG",
            "original_price": 38000,
            "sale_price": 21900,
            "discount_rate": 42,
            "badge_text": "🚀 반값 핫딜",
            "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop",
            "affiliate_url": "https://link.coupang.com/a/bM_happycall_101rep",
            "is_pinned": False
        },
        {
            "title": "초강력 틈새 먼지제거 전동 에어더스터 무선 에어건",
            "subtitle": "캔 스프레이 그만 사세요. 100,000 RPM 강력한 바람으로 본체 청소",
            "curator_comment": "키보드 사이 과자부스러기랑 맥북 팬 청소할 때 신세계가 열립니다.",
            "affiliate_platform": "ALIEXPRESS",
            "original_price": 49000,
            "sale_price": 19800,
            "discount_rate": 60,
            "badge_text": "⚡ 가성비 1등",
            "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop",
            "affiliate_url": "https://s.click.aliexpress.com/e/_dAirDuster_101rep",
            "is_pinned": False
        },
        {
            "title": "샤오미 미지아 2세대 전동 정밀 드라이버 24종 비트 세트",
            "subtitle": "토스 10% 파괴특가! 스마트폰/노트북/안경 자가수리 종결템",
            "curator_comment": "토스페이 1초 결제로 배송비 포함 2만원 초반대. 공대생/IT 직장인 필수 소장 가성비 1등!",
            "affiliate_platform": "TOSS",
            "original_price": 45000,
            "sale_price": 21500,
            "discount_rate": 52,
            "badge_text": "⚡ 토스 10% 파괴가",
            "image_url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600&auto=format&fit=crop",
            "affiliate_url": "https://toss.im/_m/share?id=xiaomi_screwdriver_101rep",
            "is_pinned": False
        }
    ],

    # 🎭 페르소나 - 30대 직장인 생존템 / 피로회복 (@ktaehoon80)
    "OFFICE_WORKER": [
        {
            "title": "종근당건강 아임비타 이뮨샷 액상비타민 30입 기획",
            "subtitle": "오쏘몰 반값! 야근 직장인 피로회복 1등 비타민 영양제",
            "curator_comment": "야근 잦거나 월요병 심할 때 아침에 한 병 털어넣으면 밤까지 버텨집니다.",
            "affiliate_platform": "COUPANG",
            "original_price": 89000,
            "sale_price": 49900,
            "discount_rate": 44,
            "badge_text": "🚀 직장인 생존템",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&auto=format&fit=crop",
            "affiliate_url": "https://link.coupang.com/a/bM_imvita_kth80",
            "is_pinned": True
        },
        {
            "title": "닥터지 레드 블레미쉬 포맨 올인원 플루이드 150ml + 75ml 세트",
            "subtitle": "끈적임 제로! 면도 후 붉은기 진정 + 수분 보습 한 번에 해결",
            "curator_comment": "이것저것 바르기 귀찮은 남성분들 무조건 이거 쓰세요. 개기름 싹 잡아줍니다.",
            "affiliate_platform": "OLIVE_YOUNG",
            "original_price": 32000,
            "sale_price": 22400,
            "discount_rate": 30,
            "badge_text": "✨ 올영 옴므 1위",
            "image_url": "https://images.unsplash.com/photo-1526947425960-945c6e72858f?w=600&auto=format&fit=crop",
            "affiliate_url": "https://affiliate.oliveyoung.co.kr/drg_men_kth80",
            "is_pinned": False
        },
        {
            "title": "커블체어 그랜드 허리 지지 자세교정 의자 쿠션",
            "subtitle": "하루 8시간 앉아있는 직장인 허리 통증 완화 완벽 지지",
            "curator_comment": "구부정하게 일하다가 허리 삐끗한 후로 필수품 됐습니다. 자세가 절로 펴져요.",
            "affiliate_platform": "COUPANG",
            "original_price": 69000,
            "sale_price": 44900,
            "discount_rate": 35,
            "badge_text": "🚀 로켓배송",
            "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=600&auto=format&fit=crop",
            "affiliate_url": "https://link.coupang.com/a/bM_curble_kth80",
            "is_pinned": False
        },
        {
            "title": "슬림 풋레스트 인체공학 무빙 발받침대 3단계 각도조절",
            "subtitle": "토스 10% 단독할인! 다리 꼬기 방지 & 골반/허리 통증 완화",
            "curator_comment": "의자에 앉아있을 때 다리 저리고 붓는 직장인분들. 토스 공구로 만원대에 책상 밑에 두면 퇴근할 때 다리가 가볍습니다.",
            "affiliate_platform": "TOSS",
            "original_price": 39000,
            "sale_price": 18900,
            "discount_rate": 51,
            "badge_text": "⚡ 토스 10% 특가",
            "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=600&auto=format&fit=crop",
            "affiliate_url": "https://toss.im/_m/share?id=footrest_kth80",
            "is_pinned": False
        }
    ],

    # 🎭 페르소나 - 여행 / 여가 / 라이프 (@taechi.tube)
    "TRAVEL_LIFE": [
        {
            "title": "초경량 기내반입 압축 여행용 파우치 6종 세트",
            "subtitle": "캐리어 부피 50% 압축! 구김 방지 방수 오거나이저",
            "curator_comment": "여행 짐 쌀 때 이거 없으면 짐 못 쌉니다. 겨울 코트나 패딩도 납작하게 압축!",
            "affiliate_platform": "COUPANG",
            "original_price": 34000,
            "sale_price": 19800,
            "discount_rate": 42,
            "badge_text": "🚀 여행 필수템",
            "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop",
            "affiliate_url": "https://link.coupang.com/a/bM_travelpouch_taechi",
            "is_pinned": True
        },
        {
            "title": "인스탁스 미니 에보 하이브리드 즉석 폴라로이드 카메라",
            "subtitle": "레트로 감성 필름 카메라 + 스마트폰 사진 출력 프린터 겸용",
            "curator_comment": "여행지에서 찍고 마음에 드는 사진만 골라서 필름으로 뽑을 수 있어서 인생템!",
            "affiliate_platform": "OHOUSE",
            "original_price": 320000,
            "sale_price": 279000,
            "discount_rate": 13,
            "badge_text": "🏠 오늘의집 감성",
            "image_url": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&auto=format&fit=crop",
            "affiliate_url": "https://ohou.se/curator/links/taechi_evo",
            "is_pinned": False
        },
        {
            "title": "전 세계 150개국 올인원 해외여행용 고속 멀티 변환 플러그",
            "subtitle": "C타입 3포트 + USB 2포트 탑재! 어댑터 하나로 온 가족 충전",
            "curator_comment": "일본, 유럽, 동남아, 미국 어딜 가든 이 플러그 하나면 충전기 따로 필요 없습니다.",
            "affiliate_platform": "ALIEXPRESS",
            "original_price": 28000,
            "sale_price": 12800,
            "discount_rate": 54,
            "badge_text": "⚡ 54% 특가",
            "image_url": "https://images.unsplash.com/photo-1563770660941-20978e870e26?w=600&auto=format&fit=crop",
            "affiliate_url": "https://s.click.aliexpress.com/e/_dTravelAdapter_taechi",
            "is_pinned": False
        },
        {
            "title": "알루미늄 프레임 기내용 20인치 캐리어 (TSA 락 + 무소음 더블휠)",
            "subtitle": "토스 10% 단독 공구! 파손 방지 하드케이스 & 360도 부드러운 핸들링",
            "curator_comment": "토스 쉐어링크 단독 혜택으로 백화점 20만원대 퀄리티를 6만원대에 겟. 제주도/일본 갈 때 완벽!",
            "affiliate_platform": "TOSS",
            "original_price": 149000,
            "sale_price": 68000,
            "discount_rate": 54,
            "badge_text": "⚡ 토스 10% 단독",
            "image_url": "https://images.unsplash.com/photo-1565026057447-bc90a3dceb87?w=600&auto=format&fit=crop",
            "affiliate_url": "https://toss.im/_m/share?id=carrier20_taechi",
            "is_pinned": False
        }
    ]
}

ACCOUNT_CLUSTER_MAP = {
    "kth.101rep": "IT_TECH",
    "lookatmeai": "BEAUTY",
    "yr170425": "LIVING",
    "toontoooon": "TREND_TOON",
    "101rep80": "HOT_DEAL",
    "ktaehoon80": "OFFICE_WORKER",
    "taechi.tube": "TRAVEL_LIFE"
}

class PickSourcerService:
    @staticmethod
    def auto_source_for_account(db: Session, account_id: int) -> int:
        repo = Repository(db)
        account = repo.get_account(account_id)
        if not account:
            return 0
        
        clean_user = account.username.lstrip("@").strip()
        cluster_key = ACCOUNT_CLUSTER_MAP.get(clean_user)
        if not cluster_key:
            # Fallback by category/cluster
            if "IT" in (account.category or ""):
                cluster_key = "IT_TECH"
            elif "뷰티" in (account.category or ""):
                cluster_key = "BEAUTY"
            elif "살림" in (account.category or ""):
                cluster_key = "LIVING"
            elif "직장인" in (account.category or ""):
                cluster_key = "OFFICE_WORKER"
            elif "핫딜" in (account.category or "") or "가성비" in (account.category or ""):
                cluster_key = "HOT_DEAL"
            else:
                cluster_key = "TREND_TOON"
        
        items_data = CURATED_PLATFORM_CATALOG.get(cluster_key, [])
        profile = repo.get_or_create_pick_profile(account_id)

        # Ensure profile title and bio match account persona
        if not profile.title or profile.title.startswith("공식"):
            profile.title = f"{account.display_name or account.username} 큐레이션 PICK"
            profile.bio = f"{account.category} 실사용자가 직접 검증한 가성비 꿀템 모음집"
            db.commit()

        # Check existing items to prevent exact duplicates by title
        existing_items = repo.list_pick_items(account_id, active_only=False)
        existing_titles = {i.title for i in existing_items}

        added_count = 0
        for data in items_data:
            if data["title"] not in existing_titles:
                repo.add_pick_item(
                    profile_id=profile.id,
                    account_id=account.id,
                    data=data
                )
                added_count += 1
                logger.info(f"Added pick item for @{account.username}: {data['title']} ({data['affiliate_platform']})")
        
        return added_count

    @staticmethod
    def auto_source_all_accounts(db: Session) -> Dict[str, int]:
        repo = Repository(db)
        accounts = repo.list_accounts()
        results = {}
        for acc in accounts:
            cnt = PickSourcerService.auto_source_for_account(db, acc.id)
            results[acc.username] = cnt
        return results

    @staticmethod
    def pin_product_for_account(db: Session, account_id: int, product_id: int) -> bool:
        """
        When a post is published on Threads promoting a product, automatically pin that product
        to position #1 with a '⭐ 쓰레드 화제의 꿀템!' badge on the account's PICK page.
        """
        repo = Repository(db)
        product = repo.get_product(product_id)
        if not product:
            return False
        
        profile = repo.get_or_create_pick_profile(account_id)
        items = repo.list_pick_items(account_id, active_only=False)
        
        # Unpin existing items
        for it in items:
            it.is_pinned = False
        
        # Find if item already exists for this product
        target_item = next((it for it in items if it.product_id == product_id or it.title == product.name), None)
        if target_item:
            target_item.is_pinned = True
            target_item.badge_text = "⭐ 쓰레드 화제의 꿀템!"
            target_item.order_seq = 999
        else:
            discount = 0
            if product.original_price and product.original_price > product.price:
                discount = int(round((1 - product.price / product.original_price) * 100))

            repo.add_pick_item(
                profile_id=profile.id,
                account_id=account_id,
                data={
                    "product_id": product.id,
                    "title": product.name,
                    "subtitle": f"{product.shipping_type} | 실시간 검증 핫딜",
                    "curator_comment": "방금 쓰레드에서 소개해 드린 바로 그 화제의 아이템입니다!",
                    "affiliate_platform": "COUPANG" if product.source == "coupang" else "COUPANG",
                    "original_price": product.original_price,
                    "sale_price": product.price,
                    "discount_rate": discount,
                    "badge_text": "⭐ 쓰레드 화제의 꿀템!",
                    "image_url": product.image_url,
                    "affiliate_url": product.url,
                    "is_pinned": True,
                    "order_seq": 999
                }
            )
        db.commit()
        return True

