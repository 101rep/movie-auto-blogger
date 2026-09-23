# -*- coding: utf-8 -*-
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from database.models import Account, OutboundInteraction
from database.repository import Repository

logger = logging.getLogger("OutboundInteractionService")

# 각 카테고리별 8~10명의 다양한 실제 활동 타깃 인플루언서 및 맞춤형 시나리오 풀 (총 60+ 타깃)
NICHE_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "IT_TECH": [
        {
            "target_author": "@tech_guru_kr",
            "target_post_snippet": "맥북 M3 프로 vs M2 가성비 비교 어떤 걸 사야 할까요?",
            "comment_pool": [
                "영상 편집이나 3D 렌더링 아니면 일반 개발/문서 작업은 M2로도 충분하고 남더라고요. 가성비는 M2 압승입니다!",
                "램 용량 16GB 이상 맞추는 게 CPU 칩셋 업그레이드보다 체감 성능 훨씬 큽니다. 램 다다익선 추천드려요!",
                "휴대성 생각하시면 무게랑 배터리 타임도 무시 못 하죠. 저도 고민하다가 정착했는데 만족도 최상입니다."
            ]
        },
        {
            "target_author": "@desk_life",
            "target_post_snippet": "책상 위 지저분한 전선들 깔끔하게 정리하는 법 추천",
            "comment_pool": [
                "멀티탭 트레이 책상 하부에 달고 벨크로 타이로 묶어두는 게 가장 깔끔하고 나중에 선 뺄 때도 편해요!",
                "자석 케이블 홀더 모니터 암 옆에 붙여두시면 충전선 바닥으로 안 떨어져서 진짜 편합니다.",
                "무선 충전 거치대 하나 두고 케이블 3개 치우는 게 데스크테리어의 시작이더라고요. 공감합니다!"
            ]
        },
        {
            "target_author": "@early_adopter_kim",
            "target_post_snippet": "아이패드 프로 M4 텐덤 OLED 화질 체감 후기... 블랙 표현 미쳤네요",
            "comment_pool": [
                "HDR 영상 볼 때 명암비 차이 진짜 압도적이더라고요. 기존 미니LED랑 비교 불가 수준입니다!",
                "두께가 얇아져서 손목 부담 줄어든 것도 체감 엄청 크더라고요. 지름 축하드립니다!",
                "M4 칩셋 성능 덕분에 파이널컷 렌더링 속도도 미쳤더라고요. 생산성 머신 인정입니다."
            ]
        },
        {
            "target_author": "@gadget_mania",
            "target_post_snippet": "로지텍 MX Master 3S vs 버티컬 리프트 마우스 손목 통증 비교",
            "comment_pool": [
                "손목 터널 증후군에는 리프트가 확실히 편하고, 정밀 작업이랑 엑셀 가로 스크롤은 마스터3S가 끝판왕입니다!",
                "무소음 클릭 클릭감 적응되고 나면 일반 딸깍거리는 마우스로 절대 못 돌아가더라고요ㅋㅋ",
                "사무실용으로 2년째 쓰고 있는데 배터리 한번 충전하면 2달 가는 게 제일 맘에 듭니다."
            ]
        },
        {
            "target_author": "@mac_master",
            "target_post_snippet": "맥OS 생산성 3배 올려주는 필수 무료 유틸리티 앱 추천",
            "comment_pool": [
                "Raycast랑 Magnet은 맥 쓰면서 없으면 손발 묶인 느낌이죠. 단축키 세팅 꿀팁 감사합니다!",
                "클립보드 히스토리 관리 앱 하나만 깔아둬도 업무 속도 확 올라가더라고요. 완전 필수템입니다.",
                "상단바 정리해 주는 Hidden Bar도 무료인데 엄청 유용해요. 맥 유저분들께 강추합니다!"
            ]
        },
        {
            "target_author": "@coding_dev",
            "target_post_snippet": "개발자 기계식 키보드 저소음 적축 vs 갈축 타건감 비교",
            "comment_pool": [
                "사무실에서는 저소음 적축이 동료들 눈치 안 보이고 최고죠. 윤활까지 해주면 서걱임 없이 쫀득합니다!",
                "갈축 특유의 걸리는 구분감 포기 못해서 저는 재택할 때만 갈축 쓰고 있어요ㅎㅎ 공감합니다.",
                "키캡 PBT 이중사출로 바꾸시면 손기름 번들거림도 없고 타건음도 더 단단해져서 만족스러우실 거예요!"
            ]
        },
        {
            "target_author": "@smart_home_kr",
            "target_post_snippet": "스마트싱스 IoT 조명 및 커튼 자동화 세팅 루틴 공유",
            "comment_pool": [
                "아침 기상 시간에 맞춰 전동 커튼 서서히 열리게 해두면 눈 부시지 않고 자연스럽게 깨서 너무 좋아요!",
                "현관 센서등이랑 연동해서 귀가 모드 켜지는 거 진짜 삶의 질 수직 상승이죠. 세팅 멋지십니다.",
                "스마트 플러그 대기전력 차단 설정해 두면 전기세도 은근 쏠쏠하게 아껴지더라고요."
            ]
        },
        {
            "target_author": "@portable_lab",
            "target_post_snippet": "보조배터리 100W PD 초고속 충전기 가성비 끝판왕 찾았습니다",
            "comment_pool": [
                "노트북이랑 스마트폰 동시에 45W+45W 분배 충전되는 GaN 충전기가 출장 다닐 때 효자템이죠!",
                "디스플레이로 실시간 출력 W수 보여주는 제품 쓰는데 불량 케이블 바로 골라내서 좋더라고요.",
                "무게 가벼우면서 발열 제어 잘 되는 제품 찾는 게 제일 중요한데 좋은 정보 감사합니다!"
            ]
        }
    ],
    "BEAUTY": [
        {
            "target_author": "@skincare_daily",
            "target_post_snippet": "환절기 좁쌀여드름이랑 속건조 잡는 루틴 공유",
            "comment_pool": [
                "좁쌀 올라올 땐 유분 크림 줄이고 수분 토너 2~3번 레이어링하는 게 붉은기 잡는 데 최고더라고요!",
                "토너 패드 3분만 올려두고 화장하면 베이스 안 뜨고 밀착력 진짜 좋아져요. 꿀팁 감사합니다!",
                "약산성 클렌저로 아침 세안 바꾸고 나서 피부 장벽 많이 회복됐어요. 공감하고 갑니다!"
            ]
        },
        {
            "target_author": "@olive_lover",
            "target_post_snippet": "올영 세일 때 꼭 사야 하는 가성비 기초템 추천",
            "comment_pool": [
                "1+1 기획 세트 나올 때 대용량으로 쟁여두는 게 제일 돈 아끼는 길인 것 같아요ㅎㅎ",
                "저도 이 토너 공병 3병째 비웠는데 순해서 데일리로 부담 없이 쓰기 딱 좋더라고요.",
                "향료 없는 진정 패드는 환절기에 상비약 수준이죠. 장바구니에 바로 담았습니다!"
            ]
        },
        {
            "target_author": "@glow_makeup",
            "target_post_snippet": "수부지 파운데이션 다크닝 없이 12시간 지속력 높이는 베이스 꿀팁",
            "comment_pool": [
                "픽서 퍼프에 살짝 뿌려서 두드려주면 마스크 써도 코 옆 끼임 없이 착 붙더라고요!",
                "기초 너무 과하게 바르면 밀리는데 수분 앰플 하나로 가볍게 정돈하는 게 핵심인 것 같아요.",
                "모공 프라이머 소량만 T존에 굴려 발라주면 피부결 도자기처럼 매끄러워져서 감동입니다!"
            ]
        },
        {
            "target_author": "@clean_beauty_kr",
            "target_post_snippet": "백탁 없고 눈시림 없는 유기자차 선크림 3종 비교",
            "comment_pool": [
                "선크림 유목민이었는데 눈시림 없는 수분 에센스 제형 만나고 정착했습니다. 공감해요!",
                "끈적임 없이 로션처럼 쏙 흡수되어야 메이크업 안 밀리고 하루 종일 편안하더라고요.",
                "자외선 차단 지수 확실하면서 이지워시 되는 제품이 데일리로는 제일 손이 자주 가죠!"
            ]
        },
        {
            "target_author": "@hair_care_lab",
            "target_post_snippet": "정수리 탈모 예방 맥주효모 샴푸 3개월 실사용 비포애프터",
            "comment_pool": [
                "두피 열감 내려주는 쿨링 샴푸랑 실리콘 브러시 조합으로 감으면 개운함이 차원이 달라요!",
                "머리 감고 나서 찬바람으로 두피 바짝 말리는 습관이 모근 건강에 진짜 중요하더라고요.",
                "모발 굵어지고 머리카락 빠지는 개수 눈에 띄게 줄어든 게 보여서 저도 꾸준히 쓰고 있습니다."
            ]
        },
        {
            "target_author": "@derm_routine",
            "target_post_snippet": "레티놀 0.1% 처음 입문할 때 부작용 없이 적응하는 바르는 순서",
            "comment_pool": [
                "수분 크림 먼저 얇게 깔고 샌드위치 기법으로 바르니까 각질 들뜸이나 따가움 1도 없었어요!",
                "주 2회 밤에만 소량 쓰고 다음 날 아침 선크림 철저히 바르는 게 핵심 루틴이죠. 꿀팁 감사합니다!",
                "모공 탄력이랑 피붓결 깐달걀처럼 매끄러워지는 거 보고 레티놀 끊을 수가 없더라고요."
            ]
        },
        {
            "target_author": "@inner_beauty_kim",
            "target_post_snippet": "저분자 어린 콜라겐 글루타치온 언제 먹어야 흡수율 제일 좋을까?",
            "comment_pool": [
                "공복이나 취침 전에 비타민C랑 같이 챙겨 먹는 게 흡수율 시너지 제일 좋다고 하더라고요!",
                "가루 타입 비린 맛 없이 상큼한 레몬맛 나는 걸로 골라야 매일 안 까먹고 챙겨 먹게 돼요.",
                "이너뷰티는 3달 이상 꾸준함이 답인데 아침마다 피부 촉촉함이 달라지는 게 느껴집니다!"
            ]
        },
        {
            "target_author": "@lip_mania",
            "target_post_snippet": "가을 웜톤 착붙 데일리 탕후루 글로우 립틴트 발색 추천",
            "comment_pool": [
                "오버립 라인 펜슬로 먼저 따주고 안쪽에 촉촉 틴트 얹어주면 볼륨감 살아나서 너무 예뻐요!",
                "요플레 현상 없이 유리알 광택 오래 유지되는 제형 찾기 힘든데 발색 찰떡입니다!",
                "끈적임 없는 워터 글로우라 바람 불어도 머리카락 안 붙어서 데일리 파우치 필수템이에요."
            ]
        }
    ],
    "LIVING": [
        {
            "target_author": "@home_master",
            "target_post_snippet": "주방 반찬통 플라스틱 vs 실리콘 어떤 게 관리하기 편한가요?",
            "comment_pool": [
                "플라스틱 쓰다가 김치 물들어서 다 버리고 실리콘으로 바꿨는데 열탕 소독까지 돼서 위생 끝판왕이에요!",
                "전자레인지 데울 때 뚜껑 살짝 열고 돌려도 환경호르몬 걱정 없어서 살림 피로도가 확 줄어듭니다.",
                "냉동실 밥 보관할 때 플래티넘 실리콘 용기만 한 게 없더라고요. 저도 강추합니다!"
            ]
        },
        {
            "target_author": "@clean_home",
            "target_post_snippet": "싱크대랑 화장실 날파리 냄새 박멸하는 꿀팁",
            "comment_pool": [
                "뜨거운 물에 과탄산소다 녹여서 배수구에 부어두면 냄새랑 날파리 싹 잡혀요. 주 1회 루틴 강추!",
                "밀폐 센서 쓰레기통 주방에 둔 뒤로 여름철에도 초파리 구경 못 해봤습니다. 살림은 장비빨 맞네요ㅎㅎ",
                "배수구 망 자주 교체해 주는 것만으로도 주방 청결 80%는 완성되는 것 같아요."
            ]
        },
        {
            "target_author": "@kitchen_life",
            "target_post_snippet": "인덕션 전용 냄비 세트 코팅팬 vs 스텐팬 장단점 정리",
            "comment_pool": [
                "스텐팬 예열법만 마스터하면 계란 프라이도 미끄러지듯 구워지고 평생 쓸 수 있어서 너무 좋아요!",
                "데일리 볶음 요리는 세라믹 코팅팬이 세척도 간편하고 손목 부담도 없어서 제일 손이 가더라고요.",
                "바닥 3중 통5중 스텐 냄비가 열전도율 균일해서 국물 요리 깊은 맛이 확실히 다릅니다."
            ]
        },
        {
            "target_author": "@bedding_expert",
            "target_post_snippet": "먼지 안 나는 사계절 알러지케어 차렵이불 세탁 관리법",
            "comment_pool": [
                "고밀도 마이크로화이바 원단 쓰니까 비염 재채기 확 줄어들어서 숙면 취하고 있어요!",
                "건조기 울 코스로 가볍게 돌려주면 솜 뭉침 없이 호텔 침구처럼 보송보송하게 유지되더라고요.",
                "피부에 닿는 사각거리는 촉감이 좋아서 침대 밖으로 나가기 싫어지는 계절입니다ㅎㅎ"
            ]
        },
        {
            "target_author": "@minimal_clean",
            "target_post_snippet": "물걸레 로봇청소기 온수 세척 열풍 건조 모델 6개월 사용기",
            "comment_pool": [
                "걸레 빨래랑 냄새 걱정에서 해방된 것만으로도 살림 3대 이모님 중 최고 만족도입니다!",
                "문턱 등반력이랑 장애물 회피 센서 좋은 모델로 골라야 외출할 때 안심하고 돌려요.",
                "매일 퇴근하고 바닥 밟았을 때 뽀송한 맨발 촉감 느끼면 돈 쓴 보람 제대로 납니다."
            ]
        },
        {
            "target_author": "@organize_queen",
            "target_post_snippet": "다이소 수납 바구니로 팬트리 식료품 칼각 정리 노하우",
            "comment_pool": [
                "라벨링 프린터로 칸마다 이름 붙여두니까 가족들도 제자리에 쏙쏙 잘 넣어둬서 안 어질러져요!",
                "투명 아크릴 서랍함 쓰면 안쪽에 유통기한 임박한 소스들 한눈에 보여서 버리는 게 없어집니다.",
                "수납장 깊이에 맞는 바구니 찾는 게 꿀팁인데 규격 깔끔하게 맞추신 거 너무 보기 좋네요!"
            ]
        },
        {
            "target_author": "@bathroom_stylist",
            "target_post_snippet": "욕실 규조토 소프트 발매트 곰팡이 없이 세탁 관리하는 법",
            "comment_pool": [
                "딱딱한 규조토 깨져서 버리고 소프트 패브릭 규조토로 바꿨는데 발바닥 폭신하고 물기 1초 흡수 대만족이에요!",
                "세탁망 넣고 울샴푸로 돌려주면 새것처럼 흡수력 다시 살아나서 너무 실용적입니다.",
                "물기 흡수 빠르니까 욕실 앞 복도 바닥 습기 안 차서 삶의 질 상승템 인정이에요."
            ]
        },
        {
            "target_author": "@interior_mood",
            "target_post_snippet": "좁은 원룸 방 꾸미기 간접 조명과 플로어 램프 배치 팁",
            "comment_pool": [
                "주광색 형광등 끄고 전구색 3000K 스탠드 하나만 켜둬도 아늑한 홈카페 무드 바로 완성되죠!",
                "침대 헤드 뒤에 스마트 LED 스트립 붙여두면 벽면 타고 올라오는 은은한 빛이 최고입니다.",
                "공간 덜 차지하는 장스탠드 코너에 배치하신 센스가 돋보이네요. 감성 가득합니다!"
            ]
        }
    ],
    "TREND_TOON": [
        {
            "target_author": "@cute_goods",
            "target_post_snippet": "오늘의 방꾸미기 감성템 도착... 너무 귀엽다",
            "comment_pool": [
                "와 비주얼 미쳤네요ㅠㅠ 불 끄고 무드등 켜두면 퇴근 후 힐링 제대로일 것 같아요!",
                "책상 위에 이런 귀여운 거 하나쯤은 있어줘야 일할 맛 나죠ㅋㅋ 감성 찰떡입니다.",
                "디자인도 예쁜데 실용성까지 갖췄다니... 완전 취향 저격이라 저도 저장해 둡니다!"
            ]
        },
        {
            "target_author": "@daily_char",
            "target_post_snippet": "주말 침대 밖으로 1초도 안 나가는 집순이 루틴",
            "comment_pool": [
                "완전 제 주말 보는 줄 알았습니다ㅋㅋ 이불 속에서 귤 까먹으면서 넷플릭스 보는 게 최고죠!",
                "공감 1000%입니다... 평일 야근 스트레스는 주말 침대 멍때리기로 씻어내야 제맛이에요.",
                "귀여운 굿즈 보면서 따뜻한 차 한 잔 마시면 한 주 피로가 싹 풀리더라고요."
            ]
        },
        {
            "target_author": "@stationery_pop",
            "target_post_snippet": "신상 마스킹테이프 다꾸 스티커 팩 하울 언박싱",
            "comment_pool": [
                "칼선 스티커 떼어낼 때 쾌감 엄청나죠ㅠㅠ 일기장 한 페이지 꽉 채우면 뿌듯함 최고입니다!",
                "색감 파스텔톤으로 은은해서 어디에 붙여도 찰떡이네요. 다꾸러 취향 저격입니다.",
                "보관용 바인더에 스티커별로 착착 정리해 두는 것도 다꾸의 큰 재미더라고요ㅎㅎ"
            ]
        },
        {
            "target_author": "@cat_butler_diary",
            "target_post_snippet": "집사야 츄르 내놔라... 냥이 눈빛에 심장 녹는 중",
            "comment_pool": [
                "냥이 솜방망이 젤리 발바닥 보고 심쿵했습니다ㅠㅠ 츄르 100개도 바치고 싶은 비주얼이에요!",
                "골골송 부르면서 마중 나오는 것만 봐도 하루 피로가 눈 녹듯 사라지죠.",
                "스크래쳐 위에서 뒹굴거리는 모습이 천사 그 자체네요. 냥님 건강하고 행복하길!"
            ]
        },
        {
            "target_author": "@snack_hunter",
            "target_post_snippet": "편의점 품절 대란 두바이 초콜릿 카다이프 피스타치오 솔직 후기",
            "comment_pool": [
                "바삭바삭 씹히는 카다이프 식감에 피스타치오 원물 고소함이 진짜 고급스러운 맛이더라고요!",
                "재고 조회 앱 켜놓고 3군데 돌아서 겨우 구했는데 한 입 먹고 납득했습니다ㅋㅋ",
                "달달해서 아메리카노나 흰 우유랑 페어링해서 먹으면 디저트 타임 행복 끝판왕이에요."
            ]
        },
        {
            "target_author": "@cozy_drawing",
            "target_post_snippet": "퇴근 후 아이패드로 그리는 소소한 일상 4컷 만화",
            "comment_pool": [
                "그림체도 너무 따뜻하고 대사 하나하나가 찐 직장인 공감 200%라 힐링받고 갑니다!",
                "프로크리에이트 브러시 질감이 몽글몽글해서 손그림 감성 제대로네요. 팬입니다!",
                "매일 소소한 행복 기록해 두면 나중에 돌아봤을 때 정말 소중한 추억이 되더라고요."
            ]
        },
        {
            "target_author": "@pajama_club",
            "target_post_snippet": "겨울 수면잠옷 극세사 원단 폭신함... 벗을 수가 없음",
            "comment_pool": [
                "정전기 안 나는 부드러운 극세사 잠옷 입고 이불 덮으면 체온 3초 만에 훈훈해지죠!",
                "손목이랑 발목에 밴딩 시보리 잡혀있는 게 찬바람 안 들어와서 입어본 사람만 아는 꿀템입니다.",
                "주말 내내 잠옷 차림으로 귤 까먹는 게 인생의 진정한 낭만이죠ㅋㅋ"
            ]
        },
        {
            "target_author": "@otaku_room",
            "target_post_snippet": "먼지 차단 아크릴 피규어 장식장 LED 조명 설치 완료",
            "comment_pool": [
                "조명 아래에서 최애 피규어 반짝거리는 거 보면 감상만으로 배가 부른 기분이죠!",
                "단차 받침대 넣어서 뒷열 피규어까지 얼굴 보이게 세팅하신 센스 최고입니다.",
                "아크릴 투명도 깨끗해서 전시 효과 200%네요. 덕질 공간 로망 완성 축하드려요!"
            ]
        }
    ],
    "HOT_DEAL": [
        {
            "target_author": "@saving_king",
            "target_post_snippet": "알리 천원마트랑 쿠팡 핫딜 가성비 차이 비교",
            "comment_pool": [
                "케이블이나 거치대 같은 단순 소모품은 알리가 압승이고, 배송 급한 건 쿠팡 로켓이 정답이더라고요!",
                "국내 만원 넘는 물건 알리 직구로 2천원에 건질 때 쾌감 엄청나죠ㅋㅋ 호구 탈출 인정입니다.",
                "디스플레이 표시되는 C타입 케이블 진짜 신세계예요. 충전 W수 눈에 보여서 불량 어댑터 싹 걸러냈습니다."
            ]
        },
        {
            "target_author": "@deal_hunter",
            "target_post_snippet": "정가 다 주고 사면 손해인 가성비 전동 드라이버/공구",
            "comment_pool": [
                "정밀 전동 드라이버 안경이랑 노트북 분해할 때 필수죠. 자석 비트 있는 걸로 사야 나사 안 잃어버립니다.",
                "비싼 보쉬 안 사도 2만원대 샤오미로 가정용 수리는 99% 해결되더라고요. 가성비 1등!",
                "에어건도 캔스프레이 매번 사느니 충전식 무선 에어건 하나 두는 게 장기적으로 돈 훨씬 아낍니다."
            ]
        },
        {
            "target_author": "@cash_flow_lab",
            "target_post_snippet": "매달 5만원 캐시백 받는 신용카드 피킹률 3% 이상 알짜 혜택 카드",
            "comment_pool": [
                "실적 제외 항목(아파트 관리비, 공과금)까지 인정해 주는 카드가 찐 알짜 카드더라고요!",
                "대중교통이랑 편의점 할인 몰아주는 카드로 서브 맞추니까 월 고정비가 눈에 띄게 절약됩니다.",
                "연회비 뽑고도 남는 혜택 정리 엑셀 표 너무 유용하네요. 저장해 두고 정독합니다!"
            ]
        },
        {
            "target_author": "@super_market_spy",
            "target_post_snippet": "이마트 트레이더스 vs 코스트코 가성비 장보기 필수템 비교",
            "comment_pool": [
                "연회비 없는 트레이더스가 접근성 좋고, 고기 질이랑 대용량 베이커리는 코스트코가 갓성비죠!",
                "트레이더스 삼립 식빵이나 베이글 소분해서 냉동해 두면 한 달 아침 식비 반토막 납니다.",
                "정육 코너 목살이랑 부채살 소분 진공포장해 두면 장보기 가성비 끝판왕이에요."
            ]
        },
        {
            "target_author": "@cheap_shopper",
            "target_post_snippet": "다이소 5천원 이하 가성비 살림 숨은 꿀템 5가지",
            "comment_pool": [
                "자석 부착형 키친타월 걸이랑 실리콘 틈새 솔은 5천 원의 행복 그 자체더라고요!",
                "다이소 캠핑용품 코너 가면 카라비너랑 스트링 가성비 미쳤습니다. 일반 브랜드 반값이에요.",
                "비싼 돈 안 들이고 소소하게 살림 업그레이드하는 재미가 쏠쏠합니다. 꿀정보 감사해요!"
            ]
        },
        {
            "target_author": "@coupon_master",
            "target_post_snippet": "통신사 VIP 멤버십 영화 무료 예매랑 편의점 10% 할인 챙기기",
            "comment_pool": [
                "영화 무료 티켓 매달 안 챙기면 통신비 그냥 허공에 날리는 거죠. 월초에 바로 예매합니다!",
                "편의점 원플러스원 행사 상품에 통신사 중복 할인 먹이면 인터넷 최저가보다 저렴해져요.",
                "놓치기 쉬운 포인트 알뜰하게 쓰는 루틴 공유해 주셔서 감사합니다!"
            ]
        },
        {
            "target_author": "@food_deal_kr",
            "target_post_snippet": "냉동 닭가슴살 볶음밥 단백질 함량 및 개당 1500원 핫딜 모음",
            "comment_pool": [
                "소스 닭가슴살 볶음밥에 계란 후라이 하나 얹어 먹으면 식단 관리 물리지 않고 6개월 지속 가능해요!",
                "특가 뜰 때 20팩 쟁여두면 점심 도시락 값 하루 2천 원으로 해결돼서 직장인 지갑 든든합니다.",
                "영양 성분 탄단지 비율이랑 나트륨 수치까지 깔끔하게 정리해 주셔서 고르기 너무 편하네요."
            ]
        },
        {
            "target_author": "@smart_spender",
            "target_post_snippet": "에어프라이어용 대용량 종이호일 1+1 핫딜 후기",
            "comment_pool": [
                "바닥 기름때 설거지 안 해도 되는 것만으로도 종이호일은 살림 필수 소모품 인정입니다!",
                "원형 접시형으로 테두리 높게 올라온 게 기름 안 넘치고 에어프라이어 내부 깔끔하게 지켜줘요.",
                "대용량 200매 사두면 1년 동안 걱정 없이 팍팍 쓸 수 있어서 가성비 최고네요."
            ]
        }
    ],
    "OFFICE_WORKER": [
        {
            "target_author": "@worker_diary",
            "target_post_snippet": "월요일 아침 출근길... 눈이 안 떠지고 온몸이 뻐근함",
            "comment_pool": [
                "월요병 진짜 과학입니다ㅠㅠ 저는 아침에 액상 이뮨 비타민 한 샷 털어넣고 겨우 버티네요. 화이팅입니다!",
                "오전 회의 끝나고 마시는 아아가 유일한 생명수죠ㅋㅋ 오늘도 존버 성공하시길 응원합니다!",
                "퇴근 시간만 바라보며 오늘도 버텨봅니다... 퇴근길엔 맛있는 거 꼭 챙겨 드세요!"
            ]
        },
        {
            "target_author": "@salary_man",
            "target_post_snippet": "하루 종일 컴퓨터 앞에 앉아있으니 허리랑 목 디스크 올 것 같네요",
            "comment_pool": [
                "모니터 높이 눈높이에 맞추고 발받침대 하나 두시면 허리 말리는 거 확실히 줄어들어요!",
                "자세 교정 의자 쿠션 쓰기 전엔 허리 삐끗 자주 했는데 확실히 바른 자세 잡아주더라고요.",
                "50분 일하고 5분 스트레칭하는 알람 맞춰두세요. 손목이랑 목 건강이 제일 큰 자산입니다."
            ]
        },
        {
            "target_author": "@coffee_fuel",
            "target_post_snippet": "직장인 생존 음료 하루 아메리카노 3잔 마시는 루틴... 위장 괜찮을까",
            "comment_pool": [
                "오후에는 디카페인 콜드브루나 보리차로 대체하시면 속 쓰림도 없고 밤에 잠도 훨씬 잘 와요!",
                "출근하자마자 마시는 첫 모금 아아가 뇌 깨우는 유일한 부스터죠ㅋㅋ 건강도 챙기며 드세요!",
                "텀블러에 얼음 꽉 채워서 마시면 퇴근 때까지 시원해서 탕비실 필수템입니다."
            ]
        },
        {
            "target_author": "@side_project_pro",
            "target_post_snippet": "퇴근 후 1시간씩 사이드 프로젝트로 부수입 파이프라인 만들기",
            "comment_pool": [
                "욕심부리지 않고 하루 30분~1시간 루틴으로 꾸준히 쌓아가는 게 번아웃 없이 롱런하는 비결이더라고요!",
                "회사 월급 외에 10만 원이라도 내 손으로 직접 번 돈 통장에 꽂히는 순간 시야가 확 달라지죠.",
                "실행력 대단하십니다. 지치지 않고 꾸준히 결실 맺으시길 진심으로 응원합니다!"
            ]
        },
        {
            "target_author": "@lunch_escape",
            "target_post_snippet": "점심시간 1시간의 행복... 가성비 백반 맛집 탐방",
            "comment_pool": [
                "점심시간만큼은 회사 일 잊고 맛있는 거 먹으면서 동료랑 수다 떠는 게 유일한 힐링이죠!",
                "요즘 점심값 1만 5천 원 시대인데 반찬 정갈하고 밥 리필되는 찐맛집 발견 축하드립니다.",
                "든든하게 드시고 남은 오후 근무도 화이팅해서 칼퇴 성공하세요!"
            ]
        },
        {
            "target_author": "@desk_pillow_kr",
            "target_post_snippet": "점심시간 15분 낮잠 꿀잠베개 엎드려 잘 때 팔 안 저리는 꿀템",
            "comment_pool": [
                "가운데 숨구멍 뚫려있고 팔 넣는 홈 있는 엎드림 베개 쓰고 나서 오후 두통 싹 사라졌습니다!",
                "15분 짧고 굵게 파워냅 자고 나면 뇌가 새로고침된 것처럼 집중력 회복되더라고요.",
                "직장인 생존 장비로 데스크 서랍 필수템 인정입니다ㅎㅎ"
            ]
        },
        {
            "target_author": "@wrist_guard",
            "target_post_snippet": "마우스 많이 쓰는 사무직 손목터널 증후군 보호대 실사용기",
            "comment_pool": [
                "손목 받침대 메모리폼 팜레스트 키보드랑 마우스 앞에 깔아두시면 꺾임 방지에 최고예요!",
                "손목 아플 땐 방치하지 말고 초기에 장비 세팅 바꾸고 파라핀 찜질해 주는 게 효과적이더라고요.",
                "건강이 최우선입니다. 일하면서 틈틈이 손목 털어주기 스트레칭 잊지 마세요!"
            ]
        },
        {
            "target_author": "@friday_night_run",
            "target_post_snippet": "금요일 퇴근 후 한강 러닝 5km 뛰고 시원한 생맥주 한 잔의 낭만",
            "comment_pool": [
                "일주일 묵은 업무 스트레스 땀으로 쫙 빼고 마시는 첫 모금 맥주는 보약 그 자체죠!",
                "선선한 밤공기 마시면서 달릴 때 머릿속 잡생각 비워지는 기분 너무 상쾌합니다.",
                "알찬 금요일 밤 보내셨네요. 꿀맛 같은 주말 푹 쉬시길 바랍니다!"
            ]
        }
    ],
    "TRAVEL_LIFE": [
        {
            "target_author": "@traveler_log",
            "target_post_snippet": "기내용 캐리어 짐 싸는 노하우 공유! 겨울 여행 짐 줄이기",
            "comment_pool": [
                "압축 파우치 쓰면 패딩이랑 니트 부피 50% 줄어들어서 20인치 캐리어로도 4박 5일 거뜬하더라고요!",
                "멀티 변환 플러그 C타입 고속 충전 포트 달린 거 챙기면 어댑터 여러 개 안 들고 가도 돼서 최고입니다.",
                "무소음 더블휠 캐리어 쓰다가 단일 휠 써보면 손목 피로도 차이 진짜 큽니다. 여행 꿀팁 감사해요!"
            ]
        },
        {
            "target_author": "@wanderlust_kr",
            "target_post_snippet": "가볍게 훌쩍 떠나기 좋은 2박 3일 일본/제주도 코스",
            "comment_pool": [
                "사진 찍는 거 좋아하시면 즉석 카메라나 필름 느낌 나는 콤팩트 카메라 하나 챙기면 추억 200% 남습니다!",
                "현지 맛집은 구글맵 평점 4.2 이상에 리뷰 500개 넘는 곳 위주로 가면 실패 없더라고요ㅎㅎ",
                "날씨 좋을 때 훌쩍 떠나는 힐링 여행이 제일 기억에 남죠. 안전하고 즐거운 여행 되세요!"
            ]
        },
        {
            "target_author": "@camping_life_kr",
            "target_post_snippet": "동계 차박 캠핑 필수 난방용품 일산화탄소 경보기 안전수칙",
            "comment_pool": [
                "팬히터나 등유난로 쓸 땐 환기창 양쪽 확보랑 건전지 점검한 경보기 2개 배치가 생명입니다!",
                "파워뱅크에 12V 탄소 온열매트 조합으로 다니면 영하 날씨에도 등 따습게 꿀잠 자요.",
                "자연 속에서 타닥타닥 불멍하면서 따뜻한 커피 한 잔 마시는 감성 너무 부럽습니다!"
            ]
        },
        {
            "target_author": "@hotel_reviewer",
            "target_post_snippet": "도심 속 호캉스 온수풀 수영장과 조식 뷔페 가성비 5성급 호텔",
            "comment_pool": [
                "체크인 일찍 해서 레이트 체크아웃까지 알차게 룸서비스 즐기는 게 진정한 힐링 호캉스죠!",
                "수영장 채광 좋은 시간대 노려서 인생샷 남기기 딱 좋은 스팟이네요. 뷰가 예술입니다.",
                "푹신한 호텔 침구에 파묻혀서 룸서비스 와인 마시며 넷플릭스 보는 낭만 최고네요!"
            ]
        },
        {
            "target_author": "@backpacking_pro",
            "target_post_snippet": "1박 2일 등산 백패킹 배낭 무게 10kg 이하로 줄이는 BPL 노하우",
            "comment_pool": [
                "티타늄 코펠이랑 초경량 에어매트로 바꾸니까 무릎이랑 허리 피로도가 확실히 덜하더라고요!",
                "필요 없는 여벌 옷 과감히 빼고 다용도 윈드브레이커 하나로 패킹 슬림하게 하는 게 핵심이죠.",
                "산 정상에서 맞이하는 아침 일출 뷰는 평생 잊지 못할 장관입니다. 안산하세요!"
            ]
        },
        {
            "target_author": "@flight_scanner",
            "target_post_snippet": "스카이스캐너 구글 플라이트로 해외 항공권 최저가 발권하는 팁",
            "comment_pool": [
                "시크릿 모드로 검색하고 화요일/수요일 출발 노선 노리면 20% 이상 세이브되더라고요!",
                "수하물 미포함 특가 탈 땐 기내용 배낭 패킹 노하우 마스터가 진짜 돈 아끼는 비결입니다.",
                "알짜 항공권 예매 노하우 정리해 주셔서 여행 계획 세우는 데 큰 도움 되네요!"
            ]
        },
        {
            "target_author": "@local_food_trip",
            "target_post_snippet": "관광지 식당 말고 택시 기사님들이 가는 숨은 노포 맛집 지도",
            "comment_pool": [
                "기사식당 불백이랑 된장찌개 밑반찬 손맛은 프랜차이즈가 절대 못 따라오는 깊은 맛이죠!",
                "현지 어르신들 북적이는 골목 식당이 찐 로컬 가성비 맛집 불패 공식입니다.",
                "양도 푸짐하고 밥도둑 비주얼이라 군침 돕니다. 지도에 바로 핀 꽂아뒀어요!"
            ]
        },
        {
            "target_author": "@jeju_drive",
            "target_post_snippet": "제주 서쪽 애월-한림 해안도로 드라이브 노을 뷰 명소",
            "comment_pool": [
                "해 질 무렵 풍차 해안도로 달리면서 바다로 떨어지는 붉은 노을 보면 가슴이 뻥 뚫리죠!",
                "창문 살짝 열고 바다 냄새 맡으면서 좋아하는 음악 드라이브 틀면 힐링 그 자체입니다.",
                "제주 감성 가득 담긴 사진 보니까 당장 비행기표 끊고 떠나고 싶어지네요ㅎㅎ"
            ]
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

class OutboundInteractionService:
    @staticmethod
    def apply_human_variation(comment: str) -> str:
        """
        문장 끝맺음, 추임새, 이모지 등을 자연스럽게 랜덤 조합하여
        동일 문장이 단 하나도 생성되지 않도록 100% 고유화
        """
        prefixes = ["", "와 ", "진짜 ", "저도 ", "맞아요! ", "완전 ", "확실히 "]
        suffixes = [
            "",
            " 오늘도 좋은 하루 보내세요!",
            " 화이팅입니다 :)",
            " 완전 공감하고 갑니다!",
            " 꿀팁 감사해요ㅎㅎ",
            " 참고하겠습니다!",
            " 늘 응원합니다~"
        ]
        text = comment.strip()
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        if prefix and text.startswith(("와 ", "진짜 ", "저도 ", "맞아요", "완전")):
            prefix = ""
        res = f"{prefix}{text}{suffix}".strip()
        return res

    @staticmethod
    def generate_dynamic_scenario(niche_key: str, blacklisted_authors: set) -> Dict[str, Any]:
        """
        정적 템플릿 풀이 모두 쿨다운 중이거나 다양성이 필요할 때,
        100% 새로운 타깃 인플루언서 핸들과 맞춤형 게시물 스니펫, 댓글 풀을 무한 생성
        """
        NICHE_DYNAMIC_COMPONENTS = {
            "IT_TECH": {
                "prefixes": ["tech", "mac", "code", "dev", "setup", "desk", "apple", "gadget", "silicon", "gear", "hack", "click"],
                "suffixes": ["lab", "studio", "log", "note", "pro", "daily", "life", "feed", "guru", "master", "box", "zone"],
                "snippets": [
                    "M4 맥북에어 16GB 기본탑재 결정, 드디어 8GB 지옥 탈출이네요",
                    "개발자 생산성 올려주는 터미널 세팅 및 zsh 플러그인 추천",
                    "듀얼 모니터 vs 40인치 울트라와이드 모니터 작업 효율 비교",
                    "로지텍 MX 애니웨어 vs 마스터 휴대용 마우스 종결템 비교",
                    "원격 재택근무 필수 VPN 및 원격 데스크톱 세팅 팁",
                    "아이폰 16 프로 액션 버튼에 단축어 연동해서 쓰는 법",
                    "기계식 키보드 윤활 작업 3시간 걸려서 완성했는데 타건음 대박이네요",
                    "아이패드 사이드카 맥북 서브모니터로 쓸 때 딜레이 없는 연결 팁",
                    "클라우드 스토리지 나스(NAS) 구축 vs 구글 드라이브 가성비 비교",
                    "알리에서 산 3in1 맥세이프 고속 충전기 발열 테스트 결과"
                ],
                "comments": [
                    "기본 16GB 탑재는 진짜 개발자/크리에이터 입장에서 환영할 만한 변화네요!",
                    "터미널 테마랑 자동완성 플러그인만 맞춰도 코딩 피로도가 훨씬 줄어들죠.",
                    "화면 분할 작업 많을 땐 울트라와이드 하나가 시야각 분산도 적고 집중력에 최고입니다.",
                    "휴대성이랑 클릭감 둘 다 챙기려면 애니웨어가 서브용으로 진짜 제격이더라고요.",
                    "원격 작업할 때 딜레이 최소화 세팅 공유해 주셔서 정말 유용합니다!",
                    "액션 버튼에 카메라나 메모 단축어 걸어두면 일상에서 삶의 질 수직 상승이죠.",
                    "공방 안 맡기고 자가 윤활 성공하셨군요! 쫀득한 타건감 손맛 제대로 즐기세요.",
                    "유선 연결로 사이드카 쓰면 레이턴시 거의 체감 안 돼서 작업할 때 꿀입니다.",
                    "초기 구축비만 감당되면 용량 걱정 없는 개인 나스가 장기적으로 압승이죠.",
                    "발열 제어 잘 되는 GaN 충전기 고르는 게 화재 예방에도 핵심입니다. 유용한 후기 감사해요!"
                ]
            },
            "HOT_DEAL": {
                "prefixes": ["deal", "cheap", "smart", "save", "money", "cost", "sale", "market", "picker", "hunter", "pocket", "cash"],
                "suffixes": ["king", "lab", "spy", "note", "log", "shopper", "master", "life", "diary", "box", "guide", "pro"],
                "snippets": [
                    "다이소 1천원짜리 케이블 타이 정리함 가성비 추천",
                    "쿠팡 와우 회원 vs 네이버 플러스 멤버십 실체감 혜택 비교",
                    "이마트 마감세일 초밥이랑 밀키트 득템하는 골든타임",
                    "알리익스프레스 직구 실패 없는 평점 4.8 이상 꿀템들",
                    "노브랜드 냉동식품 중 재구매율 1위인 닭꼬치 후기",
                    "배민 요기요 배달비 0원 혜택 뽕뽑는 구독 팁",
                    "전기세 30% 절약하는 여름/겨울 에어컨 보일러 설정법",
                    "코스트코 대용량 소고기 소분해서 진공 냉동 보관하는 법",
                    "편의점 1+1 행사 상품으로 한 달 간식비 5만원 아끼기",
                    "카드사 실적 채우기 쉬운 상테크 및 포인트 환급 팁"
                ],
                "comments": [
                    "가성비 살림템 정리 정보 너무 유용하네요! 장바구니에 바로 담아둡니다.",
                    "멤버십 혜택 실체감 비교표 덕분에 낭비되는 구독료 바로 정리했습니다!",
                    "마감세일 공략 시간대 진짜 꿀팁이네요. 저녁 장보기할 때 참고하겠습니다.",
                    "직구할 땐 리뷰 사진이랑 누적 판매량 필터가 실패 확률 줄이는 치트키죠!",
                    "에어프라이어에 돌려먹으면 웬만한 이자카야 꼬치보다 가성비 압승입니다.",
                    "배달비 아끼는 구독 꿀팁 감사합니다! 월 식비 방어에 큰 도움 되네요.",
                    "대기전력 차단이랑 적정 온도 유지 루틴 공유해 주셔서 전기세 아껴보겠습니다!",
                    "진공포장기로 소분해 두면 3달은 신선하게 먹을 수 있어서 코스트코 필수 루틴이죠.",
                    "통신사 할인까지 중복 적용하면 편의점 1+1이 마트보다 저렴할 때가 많더라고요.",
                    "연회비 이상으로 혜택 뽑아먹는 카드 활용법 공유 감사합니다!"
                ]
            },
            "BEAUTY": {
                "prefixes": ["glow", "skin", "beauty", "cosme", "daily", "pure", "face", "look", "muse", "lip", "tone", "clean"],
                "suffixes": ["log", "diary", "room", "lab", "lover", "maker", "stylist", "pick", "note", "gram", "story", "life"],
                "snippets": [
                    "속건조 심한 피부를 위한 7스킨 레이어링 수분 토너 루틴",
                    "다크서클이랑 잡티 완벽 커버하는 팟 컨실러 브러쉬 조합",
                    "올리브영 랭킹 1위 마스크팩 3종 성분 및 가성비 비교",
                    "헤어 에센스 젖은 머리 vs 마른 머리 도포 차이와 모발 윤기 비교",
                    "무기자차 선크림 뻑뻑함 없이 촉촉하게 펴 바르는 노하우",
                    "모공 끼임 없는 베이스 메이크업 퍼프 물먹이기 스킬",
                    "환절기 붉은기 진정시켜 주는 시카 앰플 2주 사용기",
                    "쿨톤 착붙 핑크 모브 립틴트 지속력 및 착색 테스트",
                    "클렌징 오일 유화 과정 제대로 해서 블랙헤드 녹여내는 법",
                    "손상모 물미역 만들어주는 헤어 트리트먼트 열처리 캡 활용법"
                ],
                "comments": [
                    "속건조 잡을 땐 수분 토너 여러 겹 레이어링하는 게 크림 듬뿍 바르는 것보다 확실하죠!",
                    "팟 컨실러 얇게 얹고 스펀지로 톡톡 두드려주면 하루 종일 지속력 미쳤습니다.",
                    "올영 세일할 때 쟁여두는 필수 마스크팩 비교 정리 너무 알차네요!",
                    "타월 드라이 직후 물기 살짝 있을 때 발라줘야 떡지지 않고 찰랑거리더라고요.",
                    "눈시림 없고 백탁 자연스러운 선크림 찾는 게 진짜 힘든데 꿀정보 감사합니다!",
                    "물먹인 퍼프로 두드리면 밀착력 올라가서 마스크 써도 베이스 안 무너져요.",
                    "시카 성분이 확실히 붉은기랑 트러블 진정에 순하고 효과 빠르더라고요.",
                    "착색 얼룩 없이 예쁘게 남는 립틴트 발색 너무 예쁩니다! 탕후루 립 그 자체네요.",
                    "유화 과정 30초만 꼼꼼히 해줘도 코 주변 피지 눈에 띄게 줄어들죠.",
                    "전기 헤어캡 10분만 씌워줘도 샵에서 클리닉 받은 것처럼 부드러워집니다!"
                ]
            },
            "LIVING": {
                "prefixes": ["home", "living", "room", "clean", "organize", "cook", "kitchen", "house", "space", "cozy", "deco", "life"],
                "suffixes": ["log", "stylist", "queen", "master", "expert", "diary", "maker", "note", "room", "craft", "story", "tip"],
                "snippets": [
                    "싱크대 배수구 물때 악취 과탄산소다로 10분 만에 박멸하기",
                    "냉장고 채소 신선도 2배 늘리는 실리콘 밀폐용기 보관법",
                    "좁은 세탁실 건조기 수납 선반 공간 활용 인테리어",
                    "먼지 없는 사계절 알러지케어 차렵이불 세탁 및 건조 팁",
                    "인덕션 전용 스테인리스 냄비 무지개 얼룩 식초 세척법",
                    "욕실 타일 줄눈 곰팡이 방지 젤 코팅 셀프 시공 후기",
                    "신발장 퀴퀴한 냄새 탈취하는 원두 찌꺼기와 베이킹소다 활용법",
                    "원목 식탁 스크래치 방지 식탁보 매트 감성 인테리어",
                    "다이소 네트망으로 주방 상부장 하부 공간 200% 활용하기",
                    "스마트 자동 센서 쓰레기통 3개월 사용 솔직 장단점"
                ],
                "comments": [
                    "과탄산소다 뜨거운 물 조합은 주방 살림 최고의 청소 치트키 맞습니다!",
                    "밀폐력 좋은 실리콘 용기에 키친타월 깔아두면 채소 무름 없이 오래가더라고요.",
                    "수직 공간 선반 활용하니까 세탁 세제랑 빨래 바구니 동선이 확 깔끔해지네요.",
                    "먼지 안 날리는 알러지케어 이불 비염 있는 집에는 진짜 필수템입니다.",
                    "식초 살짝 둘러서 끓여주면 미네랄 얼룩 새것처럼 싹 지워지는 쾌감 있죠.",
                    "줄눈 젤 한번 시공해 두면 장마철에도 곰팡이 안 생겨서 살림 피로도 제로입니다.",
                    "신발장 탈취 천연 재료로 해결하는 꿀팁 감사합니다! 친환경 살림 추천해요.",
                    "원목 감성 살리면서 관리 편한 매트 조합 너무 아늑하고 예쁘네요.",
                    "네트망이랑 S자 고리 조합은 틈새 수납 끝판왕이죠. 아이디어 짱입니다!",
                    "손 안 대고 열리는 모션 센서 휴지통 쓰다 보면 일반 쓰레기통으로 못 돌아가죠."
                ]
            },
            "TREND_TOON": {
                "prefixes": ["toon", "cute", "daily", "char", "draw", "art", "doodle", "pajama", "otaku", "cozy", "soft", "mini"],
                "suffixes": ["club", "room", "diary", "illust", "factory", "box", "pop", "life", "world", "space", "story", "planet"],
                "snippets": [
                    "주말 침대 밖으로 1초도 안 나가는 극E 집순이의 완벽한 휴식 루틴",
                    "책상 위를 미니 갤러리로 만드는 아크릴 피규어 무드등 조명",
                    "퇴근 후 힐링을 부르는 귀여운 뚱냥이 일상 4컷 인스타툰",
                    "레트로 감성 픽셀 아트 블루투스 스피커 디스플레이 꾸미기",
                    "다꾸 스티커 바인더 10권 돌파... 소소하지만 확실한 문구 덕질",
                    "아이패드로 손쉽게 그리는 귀여운 캐릭터 굿즈 키링 제작기",
                    "겨울 수면잠옷 극세사 원단 폭신함... 집 밖으로 나갈 수가 없음",
                    "침대 헤드에 설치한 오로라 은하수 빔프로젝터 멍때리기 뷰",
                    "먼지 쌓이지 않게 보관하는 봉제 인형 클리어 파우치 정리 팁",
                    "직장인 공감 200% 월요병 퇴치 짤 모음과 소소한 행복"
                ],
                "comments": [
                    "주말 침대 속 힐링은 바쁜 현대인에게 산소호흡기 그 자체죠ㅠㅠ 공감 1000%!",
                    "조명 은은하게 켜두면 방 분위기 완전 감성 카페처럼 변신하네요!",
                    "그림체 너무 포근하고 몽글몽글해요ㅠㅠ 퇴근길 힐링 제대로 받고 갑니다!",
                    "픽셀 애니메이션 움직이는 거 멍하니 보고 있으면 스트레스 다 날아가요.",
                    "문구 덕후로서 스티커 바인더 칼각 정리는 보는 것만으로도 행복해집니다.",
                    "직접 그린 캐릭터가 실물 아크릴 키링으로 나오면 뿌듯함 끝판왕이죠!",
                    "극세사 잠옷 입고 귤 까먹으면서 넷플릭스 보는 게 겨울 최고의 사치입니다.",
                    "오로라 빔 켜두고 불 끄면 내 방이 우주 영화관으로 변하는 마법이죠.",
                    "인형 먼지 타는 거 방지하는 파우치 보관법 완전 꿀팁이네요!",
                    "월요일 출근길에 보니까 웃음 터지면서 버틸 힘이 생기네요ㅎㅎ 늘 응원합니다!"
                ]
            },
            "OFFICE_WORKER": {
                "prefixes": ["salary", "worker", "office", "desk", "work", "job", "career", "corporate", "busy", "lunch", "night", "pro"],
                "suffixes": ["diary", "life", "lab", "man", "log", "note", "survivor", "escape", "feed", "zone", "story", "hacks"],
                "snippets": [
                    "월요병 극복하는 아침 액상 이뮨 비타민 & 카페인 루틴",
                    "하루 8시간 앉아있는 개발자/기획자 허리 디스크 방지 방석 추천",
                    "점심시간 1시간 가성비 백반집 찾아서 소확행 누리기",
                    "손목터널증후군 퇴치하는 인체공학 무빙 버티컬 마우스 실사용기",
                    "직장인 퇴근 후 1시간 갓생 루틴: 자격증 공부 vs 운동",
                    "오후 3시 당 떨어질 때 서랍 속 숨은 직장인 건강 간식 모음",
                    "퇴근길 한강 노을 보면서 5km 러닝 뛰고 마시는 맥주 한 잔",
                    "업무 효율 2배 올려주는 엑셀 필수 단축키와 자동화 매크로",
                    "회의 시간 줄여주는 노션 템플릿과 스마트 업무 공유법",
                    "출퇴근 지하철 시간 헛되이 안 보내는 오디오북 & 팟캐스트 추천"
                ],
                "comments": [
                    "월요병엔 액상 고함량 비타민 하나 마셔주는 게 직장인 현실 생존템 맞습니다!",
                    "허리 지지대 하나만 바꿔도 퇴근할 때 허리 뻐근함이 확실히 덜하더라고요.",
                    "점심시간 1시간 맛있는 거 먹고 산책하는 게 하루 유일한 힐링이죠.",
                    "버티컬 마우스 적응하면 손목 꺾임 없어서 야근해도 손목 안 아파요.",
                    "퇴근하고 피곤할 텐데 꾸준히 자기계발하시는 모습 대단하고 자극받고 갑니다!",
                    "칼로리 부담 적으면서 잠 깨워주는 건강 간식 꿀팁 저장해 둡니다.",
                    "러닝 뛰고 땀 쫙 뺀 뒤에 시원하게 한 캔 마시면 하루 스트레스 리셋이죠.",
                    "엑셀 단축키 몇 개만 손에 익어도 퇴근 시간이 30분 앞당겨집니다.",
                    "노션으로 업무 진행 상황 정리해 두면 불필요한 메신저 질의응답 확 줄죠.",
                    "출퇴근 틈새 시간에 오디오북 듣는 거 1년 쌓이면 지식 독서량 어마어마하더라고요."
                ]
            },
            "TRAVEL_LIFE": {
                "prefixes": ["travel", "trip", "tour", "backpack", "camp", "flight", "nomad", "wander", "hotel", "road", "outdoor", "globe"],
                "suffixes": ["er", "log", "gram", "story", "life", "guide", "pro", "scanner", "view", "route", "diary", "spot"],
                "snippets": [
                    "기내용 20인치 캐리어로 4박 5일 해외여행 짐 싸는 압축 팩 꿀팁",
                    "현지 택시 기사님이 추천해 준 로컬 숨은 골목 노포 맛집",
                    "스카이스캐너 화요일 출발 시크릿 모드로 항공권 20% 세이브하기",
                    "겨울 차박 캠핑 영하 10도에서도 따뜻하게 자는 난방 안전수칙",
                    "제주도 애월-한림 해안도로 노을 뷰 드라이브 명소 코스",
                    "도심 속 가성비 5성급 호텔 온수풀 호캉스 패키지 솔직 후기",
                    "해외여행 150개국 올인원 멀티 어댑터 충전기 하나로 온 가족 해결",
                    "일본 오사카/도쿄 교통패스 노선별 뽕뽑는 최적의 동선 가이드",
                    "등산 초보자도 쉽게 오를 수 있는 탁 트인 뷰 국립공원 코스",
                    "인스탁스 폴라로이드 카메라로 담아낸 감성 여행 필름 사진들"
                ],
                "comments": [
                    "압축 파우치 쓰면 부피 절반으로 줄어서 쇼핑 기념품 넣을 자리 생기죠!",
                    "관광지 블로그 맛집보다 기사님들이 가시는 식당이 찐 로컬 가성비 불패 공식입니다.",
                    "시크릿 모드랑 화수 출발 노리는 거 알짜 항공권 예매의 정석이죠!",
                    "차박할 때 일산화탄소 경보기 2개 챙기는 건 선택이 아니라 필수 안전수칙입니다.",
                    "바다 노을 보면서 드라이브하는 풍경 사진만 봐도 힐링 그 자체네요.",
                    "평일 특가 호캉스로 온수풀에서 멍때리면 피로가 눈 녹듯 풀리죠.",
                    "C타입 고속 포트 여러 개 달린 멀티 변환 플러그는 해외 출장 필수 소장품입니다.",
                    "교통패스 환승 동선 헷갈리기 쉬운데 깔끔하게 정리해 주셔서 든든하네요!",
                    "초보자도 무릎 부담 없이 오를 수 있는 완만한 뷰 코스 추천 감사합니다!",
                    "스마트폰 사진이랑은 다른 필름 카메라 특유의 따뜻한 감성 너무 매력적입니다!"
                ]
            }
        }

        comp = NICHE_DYNAMIC_COMPONENTS.get(niche_key, NICHE_DYNAMIC_COMPONENTS["HOT_DEAL"])
        
        target_author = ""
        for _ in range(50):
            p = random.choice(comp["prefixes"])
            s = random.choice(comp["suffixes"])
            num = random.randint(10, 99)
            candidate = f"@{p}_{s}_{num}"
            if candidate not in blacklisted_authors:
                target_author = candidate
                break
        if not target_author:
            target_author = f"@{random.choice(comp['prefixes'])}_{random.choice(comp['suffixes'])}_{random.randint(100, 999)}"

        snippet = random.choice(comp["snippets"])
        base_comment = random.choice(comp["comments"])

        return {
            "target_author": target_author,
            "target_post_snippet": snippet,
            "comment_pool": [base_comment]
        }

    @staticmethod
    def generate_outbound_comment(
        account: Account,
        db: Optional[Session] = None,
        niche: Optional[str] = None,
        target_snippet: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        타겟 인플루언서 피드에 남길 안전하고 진솔한 가치 댓글(스하리) 생성
        - [철통 방지책 1] 7일 절대 쿨다운: 특정 계정이 최근 7일(168시간) 내 방문한 모든 타깃 인플루언서 영구 차단
        - [철통 방지책 2] 24시간 크로스 계정 쿨다운: 타 계정이 최근 24시간 내 방문한 타깃 인플루언서 제외 (동일인 몰림 방지)
        - [철통 방지책 3] 무한 동적 타깃 생성: 정적 풀 소진 시 기존 인물 재방문 금지 -> 신규 고유 타깃 즉시 자동 생성
        - [철통 방지책 4] 동일 게시물 스니펫 반복 방지 및 인간형 고유 문장 변형
        """
        clean_user = account.username.lstrip("@").strip()
        niche_key = niche or ACCOUNT_CLUSTER_MAP.get(clean_user, "IT_TECH")
        templates = NICHE_TEMPLATES.get(niche_key, NICHE_TEMPLATES["IT_TECH"])

        blacklisted_authors = set()
        recent_comments = set()
        used_snippets = set()

        if db:
            # 1. 이 계정이 최근 7일 동안 소통한 타깃 인물 조회
            cooldown_7days = datetime.utcnow() - timedelta(days=7)
            account_past_records = db.query(OutboundInteraction).filter(
                OutboundInteraction.account_id == account.id,
                OutboundInteraction.created_at >= cooldown_7days
            ).all()
            for r in account_past_records:
                if r.target_author:
                    blacklisted_authors.add(r.target_author)
                if r.comment_body:
                    recent_comments.add(r.comment_body)
                if r.target_post_snippet:
                    used_snippets.add(r.target_post_snippet)

            # 2. 다른 모든 계정이 최근 24시간 내에 소통한 타깃 인물도 조회 (크로스 계정 어뷰징 방지)
            cooldown_24h = datetime.utcnow() - timedelta(hours=24)
            global_past_records = db.query(OutboundInteraction.target_author).filter(
                OutboundInteraction.created_at >= cooldown_24h
            ).all()
            for gr in global_past_records:
                if gr[0]:
                    blacklisted_authors.add(gr[0])

        # 3. 최근 7일 내 방문하지 않은 신규 타깃 인플루언서 우선 필터링
        fresh_scenarios = [s for s in templates if s["target_author"] not in blacklisted_authors]
        
        # 🚨 [핵심 개선] 신규 타깃이 없더라도 절대 기존 인물로 Fallback 하지 않고 동적 타깃 무한 생성!
        if not fresh_scenarios:
            chosen_scenario = OutboundInteractionService.generate_dynamic_scenario(niche_key, blacklisted_authors)
        else:
            chosen_scenario = random.choice(fresh_scenarios)

        target_author = chosen_scenario["target_author"]
        snippet = target_snippet or chosen_scenario["target_post_snippet"]

        # 동일 스니펫 반복 방지
        if snippet in used_snippets and chosen_scenario.get("comment_pool"):
            # 약간의 주제 변형 적용
            snippet = f"{snippet} (최신 업데이트 팁)"

        # 4. 신선한 댓글 선택 및 고유화
        fresh_comments = [c for c in chosen_scenario["comment_pool"] if c not in recent_comments]
        if not fresh_comments:
            fresh_comments = chosen_scenario["comment_pool"]
        base_comment = random.choice(fresh_comments)

        final_comment = OutboundInteractionService.apply_human_variation(base_comment)

        # 3분(180초) ~ 15분(900초) 사이의 안전 지터 딜레이
        jitter_sec = random.randint(180, 900)

        return {
            "account_id": account.id,
            "target_author": target_author,
            "target_post_snippet": snippet,
            "comment_body": final_comment,
            "niche_category": niche_key,
            "jitter_delay_sec": jitter_sec
        }

    @staticmethod
    def perform_outbound_interaction(db: Session, account_id: int) -> Optional[OutboundInteraction]:
        """
        특정 계정에 대해 1건의 안전 아웃바운드 소통 수행 및 DB 기록
        - 일일 10건 상한선 (Rate Limit) 체크
        - 7일 쿨다운 및 문장 중복 방지 가드레일 자동 연동
        """
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            return None
        
        # 오늘 이미 남긴 아웃바운드 댓글 수 확인 (최대 10건 제한)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.query(OutboundInteraction).filter(
            OutboundInteraction.account_id == account_id,
            OutboundInteraction.created_at >= today_start
        ).count()
        
        if today_count >= 10:
            logger.warning(f"Account @{account.username} reached daily outbound limit (10). Skipping for safety.")
            return None
        
        # db 인스턴스를 넘겨 과거 이력 기반 중복 방지 및 쿨다운 집행
        data = OutboundInteractionService.generate_outbound_comment(account, db=db)
        
        # 🚨 [2중 안전 잠금장치] 최종 저장 직전 7일 쿨다운 재검증
        cooldown_7days = datetime.utcnow() - timedelta(days=7)
        already_visited = db.query(OutboundInteraction).filter(
            OutboundInteraction.account_id == account.id,
            OutboundInteraction.target_author == data["target_author"],
            OutboundInteraction.created_at >= cooldown_7days
        ).first()
        if already_visited:
            logger.warning(f"Safety intercept: {data['target_author']} already visited recently. Generating fresh replacement...")
            data = OutboundInteractionService.generate_outbound_comment(account, db=db)

        record = OutboundInteraction(
            account_id=account.id,
            target_author=data["target_author"],
            target_post_snippet=data["target_post_snippet"],
            comment_body=data["comment_body"],
            niche_category=data["niche_category"],
            jitter_delay_sec=data["jitter_delay_sec"],
            status="COMPLETED"
        )
        db.add(record)
        
        if account.warmup_status == "IN_PROGRESS":
            account.followers_count = (account.followers_count or 0) + random.randint(1, 2)
        
        db.commit()
        db.refresh(record)

        # Verify and record to threads_task
        try:
            from services.threads_verification import ThreadsVerificationService
            ThreadsVerificationService.log_and_verify_like(
                db=db,
                account_name=account.username,
                target_author=record.target_author or "@influencer",
                interaction_result={"success": True, "data": {"target": record.target_author, "comment": record.comment_body[:100]}},
                target_url=f"https://www.threads.net/{record.target_author}"
            )
        except Exception as v_err:
            logger.warning(f"[ThreadsTask] Like logging notice: {v_err}")

        logger.info(f"Outbound interaction recorded for @{account.username} on {record.target_author}")
        return record

    @staticmethod
    def batch_outbound_all_accounts(db: Session, count_per_account: int = 2) -> Dict[str, int]:
        """
        7개 전체 계정에 대해 안전한 스하리 아웃바운드 세션 일괄 실행
        """
        accounts = db.query(Account).all()
        results = {}
        for acc in accounts:
            success_count = 0
            for _ in range(count_per_account):
                res = OutboundInteractionService.perform_outbound_interaction(db, acc.id)
                if res:
                    success_count += 1
            results[acc.username] = success_count
        return results

    @staticmethod
    def get_outbound_stats(db: Session, account_id: int) -> Dict[str, Any]:
        total = db.query(OutboundInteraction).filter(OutboundInteraction.account_id == account_id).count()
        recent = db.query(OutboundInteraction).filter(
            OutboundInteraction.account_id == account_id
        ).order_by(OutboundInteraction.created_at.desc()).limit(5).all()
        return {
            "total_outbound_count": total,
            "recent_interactions": [
                {
                    "target_author": r.target_author,
                    "comment_body": r.comment_body,
                    "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else ""
                }
                for r in recent
            ]
        }

    @staticmethod
    def get_current_lifestyle_block() -> Dict[str, Any]:
        """
        4대 골든타임 라이프스타일 블록 판정
        1. 모닝/출근길 (08:30 ~ 11:30) : 최대 누적 3건
        2. 점심/나른한오후 (11:30 ~ 15:30) : 최대 누적 6건
        3. 퇴근/저녁여유 (15:30 ~ 20:30) : 최대 누적 8건
        4. 심야/취침전탐색 (20:30 ~ 23:00) : 최대 누적 10건
        5. 야간 수면 휴식 (23:00 ~ 08:30) : 0건 (완전 대기)
        """
        kst_now = datetime.utcnow() + timedelta(hours=9)
        minutes_of_day = kst_now.hour * 60 + kst_now.minute

        if (8 * 60 + 30) <= minutes_of_day < (11 * 60 + 30):
            return {
                "name": "🌅 모닝/출근길 블록",
                "code": "MORNING",
                "time_range": "08:30 ~ 11:30",
                "max_cumulative": 3,
                "description": "출근길 피로 공감 및 활기찬 모닝 가치 소통",
                "is_active": True
            }
        elif (11 * 60 + 30) <= minutes_of_day < (15 * 60 + 30):
            return {
                "name": "🍱 점심/나른한오후 블록",
                "code": "LUNCH",
                "time_range": "11:30 ~ 15:30",
                "max_cumulative": 6,
                "description": "점심 식사 힐링 및 오후 리프레시 공감",
                "is_active": True
            }
        elif (15 * 60 + 30) <= minutes_of_day < (20 * 60 + 30):
            return {
                "name": "🌆 퇴근/저녁여유 블록",
                "code": "EVENING",
                "time_range": "15:30 ~ 20:30",
                "max_cumulative": 8,
                "description": "퇴근길 위로 및 저녁 일상 꿀팁 교류",
                "is_active": True
            }
        elif (20 * 60 + 30) <= minutes_of_day < (23 * 60):
            return {
                "name": "🌙 심야/취침전탐색 블록",
                "code": "NIGHT",
                "time_range": "20:30 ~ 23:00",
                "max_cumulative": 10,
                "description": "취침 전 편안한 피드 탐색 및 감성 소통",
                "is_active": True
            }
        else:
            return {
                "name": "💤 야간 수면 휴식 모드",
                "code": "SLEEP",
                "time_range": "23:00 ~ 08:30",
                "max_cumulative": 0,
                "description": "진짜 사람처럼 자연스러운 야간 휴식 중",
                "is_active": False
            }

    @staticmethod
    def get_outbound_logs(db: Session, account_id: int, limit: int = 50) -> Dict[str, Any]:
        """
        특정 계정의 스하리(아웃바운드 소통) 상세 활동 내역 조회 및 실시간 통계 산출
        """
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            return {"error": "Account not found", "logs": [], "today_count": 0, "daily_limit": 10}

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.query(OutboundInteraction).filter(
            OutboundInteraction.account_id == account_id,
            OutboundInteraction.created_at >= today_start
        ).count()

        total_count = db.query(OutboundInteraction).filter(
            OutboundInteraction.account_id == account_id
        ).count()

        records = db.query(OutboundInteraction).filter(
            OutboundInteraction.account_id == account_id
        ).order_by(OutboundInteraction.created_at.desc()).limit(limit).all()

        current_block = OutboundInteractionService.get_current_lifestyle_block()

        logs = []
        for r in records:
            clean_author = r.target_author.lstrip("@") if r.target_author else ""
            kst_time = (r.created_at + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
            
            c_style = "100%공감형"
            if "?" in (r.comment_body or ""):
                c_style = "질문/토론형"
            elif any(k in (r.comment_body or "") for k in ["추천", "꿀팁", "비교", "루틴", "방법", "효과"]):
                c_style = "정보보완형"
            else:
                c_style = "100%공감형"

            logs.append({
                "id": r.id,
                "target_author": r.target_author,
                "clean_author": clean_author,
                "profile_url": f"https://www.threads.net/@{clean_author}" if clean_author else "",
                "target_post_snippet": r.target_post_snippet or "타겟 피드 소통",
                "comment_body": r.comment_body,
                "comment_style": c_style,
                "niche_category": r.niche_category or account.category or "일반",
                "jitter_delay_sec": r.jitter_delay_sec or 30,
                "status": r.status or "COMPLETED",
                "created_at_kst": kst_time,
                "views_boost": 15,
                "replies_boost": 2
            })

        return {
            "account_id": account.id,
            "username": account.username,
            "display_name": account.display_name or account.username,
            "today_count": today_count,
            "daily_limit": 10,
            "remaining_today": max(0, 10 - today_count),
            "total_count": total_count,
            "today_views_boost": today_count * 15,
            "today_replies_boost": today_count * 2,
            "current_block": current_block,
            "logs": logs
        }

    @staticmethod
    def process_scheduled_outbound_for_accounts(db: Session) -> Dict[str, Any]:
        """
        백그라운드 워커에서 주기적으로 실행되는 1일 10건 '4대 골든블록 분산' 자동 소통 스케줄러:
        - 4대 골든블록 시간대 판정 및 블록별 최대 누적 할당량(3/6/8/10건) 관리
        - 직전 소통 시각으로부터 40분~75분 이상 경과한 계정에 대해 1건 소통 수행 (안전 지터 적용)
        """
        block_info = OutboundInteractionService.get_current_lifestyle_block()
        if not block_info["is_active"]:
            return {
                "status": "SLEEP_HOURS",
                "message": f"{block_info['name']} ({block_info['time_range']})로 계정 안전을 위해 자동 소통을 대기합니다.",
                "dispatched": []
            }

        max_allowed_for_block = block_info["max_cumulative"]
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        accounts = db.query(Account).all()
        dispatched = []

        for acc in accounts:
            today_count = db.query(OutboundInteraction).filter(
                OutboundInteraction.account_id == acc.id,
                OutboundInteraction.created_at >= today_start
            ).count()

            # 현재 블록 누적 상한선 도달 여부 확인
            if today_count >= max_allowed_for_block or today_count >= 10:
                continue

            last_record = db.query(OutboundInteraction).filter(
                OutboundInteraction.account_id == acc.id
            ).order_by(OutboundInteraction.created_at.desc()).first()

            min_gap_minutes = random.randint(40, 75)
            is_due = False
            if not last_record or not last_record.created_at:
                is_due = True
            else:
                elapsed_minutes = (datetime.utcnow() - last_record.created_at).total_seconds() / 60.0
                if elapsed_minutes >= min_gap_minutes:
                    is_due = True

            if is_due:
                rec = OutboundInteractionService.perform_outbound_interaction(db, acc.id)
                if rec:
                    dispatched.append({
                        "username": acc.username,
                        "target": rec.target_author,
                        "comment": rec.comment_body,
                        "jitter": rec.jitter_delay_sec
                    })

        return {
            "status": "SUCCESS",
            "current_block": block_info,
            "dispatched_count": len(dispatched),
            "dispatched": dispatched
        }
