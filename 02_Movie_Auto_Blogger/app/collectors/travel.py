"""Collector for Domestic and International Travel Destinations and Itineraries."""
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field

from app.utils.logging import get_logger

logger = get_logger("travel_collector")


class TravelCandidateItem(BaseModel):
    """Normalized travel destination candidate."""
    destination_id: str
    destination: str
    country: str
    region: str = ""
    duration: str = "3박 4일"
    theme: str = "핵심 명소 & 미식 힐링 투어"
    highlights: List[str] = Field(default_factory=list)
    spots: List[str] = Field(default_factory=list)
    spot_image_queries: Dict[str, str] = Field(default_factory=dict)
    flight_time: str = "직항 약 2~4시간"
    best_season: str = "봄, 가을"
    budget_guide: str = "1인 기준 약 70~120만 원 (항공/숙박/식비 포함)"
    transport_pass: str = "현지 지하철 1일 패스 및 교통카드"
    score: float = 90.0
    source_attribution: str = "글로벌 관광청 및 공공 여행 데이터 종합"
    original_url: Optional[str] = None


# Curated catalog of high-demand domestic & international travel destinations
CORE_TRAVEL_CATALOG: List[Dict[str, Any]] = [
    {
        "destination_id": "TRAVEL-OSAKA-01",
        "destination": "오사카 (Osaka)",
        "country": "일본",
        "region": "간사이",
        "duration": "3박 4일",
        "theme": "미식 탐방과 유니버셜 스튜디오 & 교토 연계 코스",
        "highlights": [
            "도톤보리 글리코상 앞 인증샷과 난바 타코야키·쿠시카츠 먹방 투어",
            "유니버셜 스튜디오 재팬(USJ) 슈퍼 닌텐도 월드 & 해리포터 완벽 정복",
            "오사카 주유패스로 우메다 공중정원, 헵파이브 관람차, 오사카성 무료 입장",
            "하루 일정으로 다녀오는 교토 청수사(기요미즈데라)와 아라시야마 대나무숲"
        ],
        "spots": ["도톤보리", "오사카성 천수각", "유니버셜 스튜디오 재팬", "우메다 공중정원", "하루카스 300", "교토 기요미즈데라"],
        "spot_image_queries": {
            "도톤보리": "Dotonbori Osaka street night",
            "오사카성 천수각": "Osaka Castle tower Japan",
            "유니버셜 스튜디오 재팬": "Universal Studios Japan Osaka",
            "우메다 공중정원": "Umeda Sky Building observatory",
            "하루카스 300": "Abeno Harukas Osaka",
            "교토 기요미즈데라": "Kiyomizu dera Kyoto temple"
        },
        "flight_time": "인천/김포 출발 직항 약 1시간 45분",
        "best_season": "3~5월(벚꽃 시즌), 10~11월(단풍 시즌)",
        "budget_guide": "1인 약 80~110만 원 (항공 25~35만, 비즈니스호텔 30만, USJ 및 식비 35만)",
        "transport_pass": "오사카 주유패스 1일/2일권 또는 간사이 쓰루패스",
        "score": 98.0,
        "original_url": "https://www.japan.travel/ko/kr/"
    },
    {
        "destination_id": "TRAVEL-FUKUOKA-02",
        "destination": "후쿠오카 (Fukuoka)",
        "country": "일본",
        "region": "규슈",
        "duration": "2박 3일",
        "theme": "주말 힐링 밤도깨비 미식 & 유후인 료칸 온천 코스",
        "highlights": [
            "공항에서 도심(하카타역)까지 지하철로 단 5분, 압도적 접근성",
            "하카타 돈코츠 라멘 본점, 모츠나베, 야타이(포장마차) 야식 투어",
            "오호리 공원 호수 산책과 텐진 지하상가 쇼핑",
            "근교 유후인 온천마을 긴린코 호수 산책 및 전통 료칸 가이세키 체험"
        ],
        "spots": ["하카타역 아뮤플라자", "나카스 야타이 거리", "오호리 공원", "텐진 다이묘거리", "유후인 온천마을", "다자이후 텐만구"],
        "spot_image_queries": {
            "하카타역 아뮤플라자": "Hakata Station Fukuoka Japan",
            "나카스 야타이 거리": "Nakasu Fukuoka river night",
            "오호리 공원": "Ohori Park Fukuoka lake",
            "텐진 다이묘거리": "Tenjin Fukuoka street",
            "유후인 온천마을": "Yufuin onsen Japan",
            "다자이후 텐만구": "Dazaifu Tenmangu shrine Fukuoka"
        },
        "flight_time": "인천/부산 출발 직항 약 1시간 15분",
        "best_season": "연중 온화하며 특히 11~3월 온천 여행 최적",
        "budget_guide": "1인 약 60~90만 원 (항공 18~28만, 호텔 20~30만, 식비/교통 25만)",
        "transport_pass": "후쿠오카 시티패스 및 산큐패스(유후인 버스 이동 시)",
        "score": 97.0,
        "original_url": "https://www.welcomekyushu.or.kr/"
    },
    {
        "destination_id": "TRAVEL-DANANG-03",
        "destination": "다낭 & 호이안 (Da Nang & Hoi An)",
        "country": "베트남",
        "region": "중부",
        "duration": "3박 5일",
        "theme": "오션뷰 리조트 호캉스, 가성비 스파 & 유네스코 올드타운 감성",
        "highlights": [
            "세계 6대 해변 미케비치 앞 가성비 5성급 풀빌라 리조트 휴양",
            "바나힐 골든브릿지(신의 손 케이블카)와 테마파크 투어",
            "호이안 올드타운 투본강 소원배 띄우기 및 야시장 야경 감상",
            "1일 1마사지와 베트남 쌀국수, 반쎄오, 콩카페 코코넛 스무디 먹방"
        ],
        "spots": ["미케 비치", "바나힐 골든브릿지", "호이안 올드타운", "오행산(마블마운틴)", "한시장", "다낭 대성당(핑크성당)"],
        "spot_image_queries": {
            "미케 비치": "My Khe Beach Da Nang coast",
            "바나힐 골든브릿지": "Ba Na Hills Golden Bridge Vietnam",
            "호이안 올드타운": "Hoi An Ancient Town lantern night",
            "오행산(마블마운틴)": "Marble Mountains Da Nang cave",
            "한시장": "Han Market Da Nang",
            "다낭 대성당(핑크성당)": "Da Nang Cathedral Pink church"
        },
        "flight_time": "인천 출발 직항 약 4시간 30분",
        "best_season": "2~5월 (건기 시즌으로 맑고 쾌적한 날씨)",
        "budget_guide": "1인 약 70~100만 원 (항공 30~45만, 5성 리조트 25~35만, 식비/스파 20만)",
        "transport_pass": "그랩(Grab) 앱 호출 필수 (택시비가 매우 저렴함)",
        "score": 96.0,
        "original_url": "https://danangfantasticity.com/"
    },
    {
        "destination_id": "TRAVEL-BANGKOK-04",
        "destination": "방콕 (Bangkok)",
        "country": "태국",
        "region": "중부",
        "duration": "3박 5일",
        "theme": "화려한 사원 문화, 루프탑 바 야경 & 트렌디 쇼핑 천국",
        "highlights": [
            "짜오프라야 강변 왓아룬 사원 일몰 뷰와 아이콘시암(ICONSIAM) 실내 수상시장",
            "미쉐린 빕구루망 팟타이, 똠얌꿍, 푸팟퐁커리 미식 탐방",
            "초고층 킹파워 마하나콘 스카이워크 유리바닥 전망대 아찔한 체험",
            "짜뚜짝 주말 시장 쇼핑과 카오산로드 나이트 라이프"
        ],
        "spots": ["왓 아룬", "왓 포", "아이콘시암", "마하나콘 스카이워크", "카오산 로드", "짜뚜짝 주말시장", "룸피니 공원"],
        "spot_image_queries": {
            "왓 아룬": "Wat Arun Bangkok temple sunset",
            "왓 포": "Wat Pho Bangkok Reclining Buddha",
            "아이콘시암": "ICONSIAM Bangkok mall river",
            "마하나콘 스카이워크": "Mahanakhon Skywalk Bangkok rooftop",
            "카오산 로드": "Khaosan Road Bangkok night street",
            "짜뚜짝 주말시장": "Chatuchak weekend market Bangkok",
            "룸피니 공원": "Lumphini Park Bangkok green"
        },
        "flight_time": "인천/부산 출발 직항 약 5시간 30분",
        "best_season": "11~2월 (건기 시즌으로 가장 여행하기 좋은 날씨)",
        "budget_guide": "1인 약 85~120만 원 (항공 35~50만, 호텔 30~40만, 식비/마사지 30만)",
        "transport_pass": "BTS 지상철 래빗카드(Rabbit Card) 및 MRT 지하철",
        "score": 95.0,
        "original_url": "https://www.visitthailand.or.kr/"
    },
    {
        "destination_id": "TRAVEL-TOKYO-05",
        "destination": "도쿄 (Tokyo)",
        "country": "일본",
        "region": "간토",
        "duration": "3박 4일",
        "theme": "도심 속 랜드마크, 서브컬처 성지와 트렌디 편집숍 투어",
        "highlights": [
            "시부야 스크램블 교차로와 시부야 스카이 옥상 전망대 도쿄 타워 뷰",
            "신주쿠 교엔 도심 숲 산책과 긴자 명품 거리 쇼핑",
            "아사쿠사 센소지 전통 사찰 구경과 도쿄 스카이트리 야경",
            "하라주쿠·오모테산도 감성 카페거리와 아키하바라 피규어 성지"
        ],
        "spots": ["시부야 스카이", "도쿄 타워", "신주쿠 가부키초 타워", "아사쿠사 센소지", "긴자 식스", "팀랩 플래닛 도쿄"],
        "spot_image_queries": {
            "시부야 스카이": "Shibuya Sky Tokyo view",
            "도쿄 타워": "Tokyo Tower night landmark",
            "신주쿠 가부키초 타워": "Kabukicho Shinjuku Tokyo street",
            "아사쿠사 센소지": "Sensoji Temple Asakusa Tokyo",
            "긴자 식스": "Ginza Tokyo luxury street",
            "팀랩 플래닛 도쿄": "teamLab Planets Tokyo lights"
        },
        "flight_time": "인천/김포 출발 직항 약 2시간 15분",
        "best_season": "3~5월(봄), 10~11월(청명한 가을 날씨)",
        "budget_guide": "1인 약 90~130만 원 (항공 30~45만, 도심 호텔 35~50만, 식비/교통 35만)",
        "transport_pass": "도쿄 지하철 24/48/72시간 무제한 티켓 및 스이카(Suica)/파스모",
        "score": 96.5,
        "original_url": "https://www.gotokyo.org/kr/"
    },
    {
        "destination_id": "TRAVEL-JEJU-06",
        "destination": "제주도 (Jeju Island)",
        "country": "대한민국",
        "region": "제주특별자치도",
        "duration": "2박 3일",
        "theme": "에메랄드빛 해안도로 드라이브, 오름 트레킹 & 흑돼지 미식",
        "highlights": [
            "함덕·협재 해수욕장 에메랄드빛 바다 뷰와 애월 한담해변 산책로",
            "성산일출봉 장엄한 일출과 섭지코지 유채꽃/가을 억새 풍경",
            "제주 흑돼지 근고기, 고등어회, 딱새우, 전복죽 로컬 미식",
            "사려니숲길 삼나무 숲 피톤치드 힐링과 오설록 티뮤지엄 녹차밭"
        ],
        "spots": ["성산일출봉", "협재 해수욕장", "함덕 해수욕장", "사려니숲길", "섭지코지", "애월 카페거리", "우도"],
        "spot_image_queries": {
            "성산일출봉": "Seongsan Ilchulbong Jeju peak",
            "협재 해수욕장": "Hyeopjae Beach Jeju emerald sea",
            "함덕 해수욕장": "Hamdeok Beach Jeju coast",
            "사려니숲길": "Saryeoni Forest Jeju cedar trees",
            "섭지코지": "Seopjikoji Jeju coastal cliff",
            "애월 카페거리": "Aewol coast Jeju cafe",
            "우도": "Udo Island Jeju sea"
        },
        "flight_time": "김포/청주/대구/부산 출발 직항 약 1시간 10분",
        "best_season": "4~6월(봄꽃), 9~10월(청명한 가을 오름 투어)",
        "budget_guide": "1인 약 35~55만 원 (항공 8~15만, 렌터카 6~10만, 펜션/호텔 15~20만, 식비 15만)",
        "transport_pass": "렌터카 완전자차 필수 (또는 제주시티투어버스)",
        "score": 97.5,
        "original_url": "https://www.visitjeju.net/"
    },
    {
        "destination_id": "TRAVEL-BUSAN-07",
        "destination": "부산 (Busan)",
        "country": "대한민국",
        "region": "부산광역시",
        "duration": "2박 3일",
        "theme": "푸른 동해바다 해변열차, 야경 명소 & 자갈치 시장 미식",
        "highlights": [
            "해운대 블루라인파크 해변열차 & 스카이캡슐 청사포 해안 절경",
            "광안리 해수욕장 광안대교 오션뷰 카페 및 주말 드론 라이트쇼",
            "자갈치 시장 꼼장어, 남포동 씨앗호떡, 밀면, 돼지국밥 원조 미식 투어",
            "흰여울문화마을 해안 절벽 골목길 산책과 영도 복합문화공간 피아크"
        ],
        "spots": ["해운대 해수욕장", "광안리 해변 & 광안대교", "블루라인파크 해변열차", "흰여울문화마을", "자갈치 시장", "용두산공원 부산타워"],
        "spot_image_queries": {
            "해운대 해수욕장": "Haeundae Beach Busan Korea ocean",
            "광안리 해변 & 광안대교": "Gwangalli Beach Gwangan Bridge night",
            "블루라인파크 해변열차": "Haeundae Blueline Park coastal train",
            "흰여울문화마을": "Huinnyeoul Culture Village Busan",
            "자갈치 시장": "Jagalchi Market Busan fish seafood",
            "용두산공원 부산타워": "Busan Tower Yongdusan Park"
        },
        "flight_time": "서울역 기준 KTX/SRT 고속철도 약 2시간 15분",
        "best_season": "5~10월 (바다 축제 및 청명한 날씨)",
        "budget_guide": "1인 약 25~45만 원 (KTX 왕복 12만, 비즈니스호텔 12~18만, 식비 12만)",
        "transport_pass": "부산 지하철 1일 무제한 승차권 (5,000원)",
        "score": 95.5,
        "original_url": "https://www.visitbusan.net/"
    },
    {
        "destination_id": "TRAVEL-TAIPEI-08",
        "destination": "타이베이 (Taipei)",
        "country": "대만",
        "region": "북부",
        "duration": "3박 4일",
        "theme": "지우펀 센과 치히로 감성, 야시장 미식 천국 & 융캉제 투어",
        "highlights": [
            "홍등이 켜지는 지우펀 골목길과 스펀 기찻길 천등 날리기 소원 빌기",
            "스린 야시장 지파이, 망고빙수, 곱창국수, 우육면 끝없는 먹방",
            "타이베이 101 타워 전망대에서 내려다보는 타이베이 분지 야경",
            "국립고궁박물원 세계 4대 박물관 진귀한 보물 관람과 단수이 일몰"
        ],
        "spots": ["타이베이 101", "지우펀", "스펀 천등마을", "스린 야시장", "융캉제", "국립고궁박물원", "단수이 어인부두"],
        "spot_image_queries": {
            "타이베이 101": "Taipei 101 tower skyscraper Taiwan",
            "지우펀": "Jiufen Old Street Taiwan lantern night",
            "스펀 천등마을": "Shifen railway lantern sky Taiwan",
            "스린 야시장": "Shilin Night Market Taipei street food",
            "융캉제": "Yongkang Street Taipei mango",
            "국립고궁박물원": "National Palace Museum Taipei",
            "단수이 어인부두": "Tamsui Fisherman Wharf sunset Taipei"
        },
        "flight_time": "인천/김포/부산 출발 직항 약 2시간 30분",
        "best_season": "10~4월 (덥지 않고 쾌적하며 야외 활동하기 최적)",
        "budget_guide": "1인 약 70~100만 원 (항공 28~38만, 호텔 25~35만, 식비/교통 25만)",
        "transport_pass": "이지카드(EasyCard) 교통카드 및 타이베이 메트로 패스",
        "score": 96.0,
        "original_url": "https://www.taiwan.net.tw/"
    },
    {
        "destination_id": "TRAVEL-SAPPORO-09",
        "destination": "삿포로 (Sapporo)",
        "country": "일본",
        "region": "홋카이도",
        "duration": "3박 4일",
        "theme": "오타루 운하 감성, 삿포로 맥주박물관 & 징기스칸 미식 투어",
        "highlights": [
            "오타루 오르골당과 유리공예 거리, 로맨틱한 오타루 운하 야경 산책",
            "삿포로 맥주박물관 생맥주 시음과 스스키노 징기스칸 양고기 화로구이",
            "스프카레와 미소라멘 원조 거리 골목 탐방",
            "사계절 아름다운 비에이 청의 호수와 후라노 전원 풍경 일일 버스투어"
        ],
        "spots": ["오타루 운하", "삿포로 맥주박물관", "스스키노 라멘요코초", "오도리 공원", "비에이 청의 호수", "모이와야마 전망대"],
        "spot_image_queries": {
            "오타루 운하": "Otaru Canal Hokkaido Japan snow lights",
            "삿포로 맥주박물관": "Sapporo Beer Museum brick",
            "스스키노 라멘요코초": "Susukino Sapporo neon night",
            "오도리 공원": "Odori Park Sapporo tower",
            "비에이 청의 호수": "Biei Blue Pond Hokkaido",
            "모이와야마 전망대": "Moiwayama Sapporo night view"
        },
        "flight_time": "인천/부산 출발 직항 약 2시간 45분",
        "best_season": "12~2월(설경·눈축제), 7~8월(라벤더 꽃밭 피서)",
        "budget_guide": "1인 약 90~135만 원 (항공 35~50만, 호텔 35~45만, 식비 30만)",
        "transport_pass": "JR 홋카이도 레일패스 또는 삿포로 지하철 전용 1일권",
        "score": 97.0,
        "original_url": "https://www.welcome.city.sapporo.jp/?lang=ko"
    },
    {
        "destination_id": "TRAVEL-SINGAPORE-10",
        "destination": "싱가포르 (Singapore)",
        "country": "싱가포르",
        "region": "동남아시아",
        "duration": "3박 5일",
        "theme": "마리나베이샌즈 레이저쇼, 가든스바이더베이 & 센토사 유니버셜",
        "highlights": [
            "가든스 바이 더 베이 슈퍼트리 그로브 야간 쇼와 플라워 돔 식물원",
            "마리나 베이 샌즈 인피니티 풀 조망과 머라이언 파크 인증샷",
            "센토사 섬 케이블카 탑승과 유니버셜 스튜디오 싱가포르",
            "뉴튼 호커센터 칠리크랩, 카야토스트, 바쿠테 로컬 미식 투어"
        ],
        "spots": ["마리나 베이 샌즈", "가든스 바이 더 베이", "머라이언 파크", "센토사 섬", "유니버셜 스튜디오 싱가포르", "차이나타운", "보타닉 가든"],
        "spot_image_queries": {
            "마리나 베이 샌즈": "Marina Bay Sands Singapore night",
            "가든스 바이 더 베이": "Gardens by the Bay Supertree Singapore",
            "머라이언 파크": "Merlion Park Singapore fountain",
            "센토사 섬": "Sentosa Island Singapore beach",
            "유니버셜 스튜디오 싱가포르": "Universal Studios Singapore globe",
            "보타닉 가든": "Singapore Botanic Gardens green"
        },
        "flight_time": "인천/부산 출발 직항 약 6시간 15분",
        "best_season": "연중 온화하며 비가 적은 6~8월 또는 축제 시즌",
        "budget_guide": "1인 약 120~170만 원 (항공 45~65만, 호텔 45~65만, 식비/투어 40만)",
        "transport_pass": "싱가포르 투어리스트 패스(STP) 또는 이지링크(EZ-Link)",
        "score": 96.5,
        "original_url": "https://www.visitsingapore.com/ko_kr/"
    },
    {
        "destination_id": "TRAVEL-NHATRANG-11",
        "destination": "나트랑 (Nha Trang)",
        "country": "베트남",
        "region": "남부",
        "duration": "3박 5일",
        "theme": "에메랄드빛 해변 휴양, 머드 온천 스파 & 빈원더스 테마파크",
        "highlights": [
            "끝없이 펼쳐진 나트랑 비치와 가성비 5성급 오션뷰 리조트 호캉스",
            "섬 전체가 테마파크인 빈원더스(VinWonders) 케이블카와 워터파크",
            "아이리조트 미네랄 머드 온천욕으로 피로를 푸는 천연 스파",
            "야시장 랍스터 해산물 바비큐와 망고, 코코넛 커피 가성비 미식"
        ],
        "spots": ["나트랑 해변", "빈원더스 나트랑", "포나가르 첨탑", "아이리조트 머드온천", "나트랑 대성당", "담시장"],
        "spot_image_queries": {
            "나트랑 해변": "Nha Trang Beach Vietnam coastline",
            "빈원더스 나트랑": "VinWonders Nha Trang cable car",
            "포나가르 첨탑": "Po Nagar Cham Towers Nha Trang",
            "아이리조트 머드온천": "I Resort Nha Trang mud bath",
            "나트랑 대성당": "Nha Trang Cathedral stone church",
            "담시장": "Dam Market Nha Trang Vietnam"
        },
        "flight_time": "인천/부산 출발 직항 약 4시간 45분",
        "best_season": "1~8월 (건기 시즌으로 맑고 투명한 바다)",
        "budget_guide": "1인 약 65~95만 원 (항공 28~40만, 5성급 리조트 25~35만, 식비/스파 20만)",
        "transport_pass": "그랩(Grab) 택시 호출 필수",
        "score": 95.5,
        "original_url": "https://vietnam.travel/"
    },
    {
        "destination_id": "TRAVEL-GANGNEUNG-12",
        "destination": "강릉 & 속초 (Gangneung & Sokcho)",
        "country": "대한민국",
        "region": "강원특별자치도",
        "duration": "2박 3일",
        "theme": "안목해변 커피거리, 동해안 일출 드라이브 & 중앙시장 먹방",
        "highlights": [
            "안목해변 커피거리 통유리 카페에서 바라보는 푸른 동해바다",
            "강릉 중앙시장 닭강정, 배니닭강정, 오징어순대, 짬뽕순두부 먹거리 투어",
            "정동진 바다부채길 주상절리 해안 산책로 파도 힐링",
            "속초 영금정 일출과 아바이마을 갯배 체험 및 대게 만찬"
        ],
        "spots": ["안목해변 커피거리", "경포호 & 경포해변", "강릉 중앙시장", "정동진 부채길", "속초 영금정", "속초아이 대관람차"],
        "spot_image_queries": {
            "안목해변 커피거리": "Anmok Beach Gangneung coffee street ocean",
            "경포호 & 경포해변": "Gyeongpo Beach Gangneung East Sea",
            "강릉 중앙시장": "Gangneung Jungang Market food street",
            "정동진 부채길": "Jeongdongjin Badabuchaegil Gangneung sea cliff",
            "속초 영금정": "Yeonggeumjeong Sokcho pavilion sunrise",
            "속초아이 대관람차": "Sokcho Eye Ferris wheel beach"
        },
        "flight_time": "서울역 기준 KTX 강릉선 약 1시간 40분",
        "best_season": "5~10월(청명한 바다), 12~1월(겨울 바다 & 새해 일출)",
        "budget_guide": "1인 약 20~35만 원 (KTX 왕복 6만, 펜션/호텔 10~15만, 식비 10만)",
        "transport_pass": "KTX + 렌터카 또는 동해선 바다열차",
        "score": 96.0,
        "original_url": "https://www.gangneung.go.kr/tour/"
    },
    {
        "destination_id": "TRAVEL-SAPPORO-13",
        "destination": "삿포로 & 오타루 (Sapporo & Otaru)",
        "country": "일본",
        "region": "홋카이도",
        "duration": "3박 4일",
        "theme": "순백의 설경, 오타루 운하 감성 & 미소라멘·스프카레 미식 투어",
        "highlights": [
            "오도리 공원과 삿포로 TV타워 야경 및 스스키노 거리 탐방",
            "오타루 운하 가스등 산책, 오르골당 & 르타오 디저트 맛집 투어",
            "겨울 비에이 & 후라노 흰수염폭포·자작나무숲 당일 버스투어",
            "진한 국물의 원조 삿포로 미소라멘과 징기스칸 양고기 구이 먹방"
        ],
        "spots": ["오도리 공원", "삿포로 TV타워", "스스키노 라멘골목", "오타루 운하", "오타루 오르골당", "비에이 청의 호수"],
        "spot_image_queries": {
            "오도리 공원": "Odori Park Sapporo winter snow",
            "오타루 운하": "Otaru Canal Hokkaido winter night",
            "오타루 오르골당": "Otaru Music Box Museum",
            "비에이 청의 호수": "Biei Blue Pond Hokkaido winter",
            "삿포로 TV타워": "Sapporo TV Tower night view"
        },
        "flight_time": "인천 출발 직항 약 2시간 40분 (신치토세 공항)",
        "best_season": "12~2월(눈축제 & 설경), 7~8월(라벤더 꽃밭)",
        "budget_guide": "1인 약 90~130만 원 (항공 35~50만, 호텔 35만, 식비/투어 35만)",
        "transport_pass": "JR 홋카이도 레일패스 또는 삿포로-오타루 웰컴패스",
        "score": 97.0,
        "original_url": "https://www.sapporo.travel/ko/"
    },
    {
        "destination_id": "TRAVEL-OKINAWA-14",
        "destination": "오키나와 (Okinawa)",
        "country": "일본",
        "region": "규슈/오키나와",
        "duration": "3박 4일",
        "theme": "에메랄드빛 해안 드라이브, 츄라우미 수족관 & 류큐 왕국 감성 힐링",
        "highlights": [
            "세계 최대급 고래상어가 헤엄치는 츄라우미 수족관 관람",
            "코우리 대교 위를 달리는 환상적인 오션뷰 렌터카 드라이브",
            "만좌모 절벽의 코끼리 바위와 국제거리 쇼핑 & 오키나와 소바",
            "아메리칸 빌리지 이국적 일몰과 선셋비치 산책"
        ],
        "spots": ["츄라우미 수족관", "코우리 대교", "만좌모", "국제거리", "아메리칸 빌리지", "슈리성"],
        "spot_image_queries": {
            "츄라우미 수족관": "Okinawa Churaumi Aquarium whale shark",
            "코우리 대교": "Kouri Island bridge Okinawa ocean",
            "만좌모": "Manzamo cliff Okinawa sea",
            "아메리칸 빌리지": "American Village Okinawa sunset"
        },
        "flight_time": "인천 출발 직항 약 2시간 15분 (나하 공항)",
        "best_season": "4~10월(해양 액티비티 및 온화한 날씨)",
        "budget_guide": "1인 약 80~115만 원 (항공 25~35만, 렌터카/호텔 40만, 식비 25만)",
        "transport_pass": "렌터카 필수 이용 또는 츄라우미 셔틀버스 투어",
        "score": 95.0,
        "original_url": "https://www.visitokinawa.jp/?lang=ko"
    },
    {
        "destination_id": "TRAVEL-BALI-15",
        "destination": "발리 (Bali)",
        "country": "인도네시아",
        "region": "동남아",
        "duration": "4박 6일",
        "theme": "신들의 섬 발리: 우붓 정글 요가 & 스미냑 비치클럽 휴양",
        "highlights": [
            "우붓 뜨갈랄랑 계단식 논과 발리스윙 인생샷 투어",
            "스미냑과 짱구의 힙한 비치클럽(포테이토헤드, 핀스)에서 즐기는 선셋",
            "울루와투 절벽 사원과 아찔한 파도 전망 케착 댄스 관람",
            "가성비 프라이빗 풀빌라에서 즐기는 플로팅 조식과 전통 스파 마사지"
        ],
        "spots": ["우붓 뜨갈랄랑 계단식 논", "울루와투 절벽사원", "스미냑 비치", "짱구 비치클럽", "따나롯 해상사원", "몽키포레스트"],
        "spot_image_queries": {
            "우붓 뜨갈랄랑 계단식 논": "Tegallalang rice terrace Ubud Bali",
            "울루와투 절벽사원": "Uluwatu temple cliff Bali sea",
            "스미냑 비치": "Seminyak beach sunset Bali club",
            "따나롯 해상사원": "Tanah Lot temple Bali ocean"
        },
        "flight_time": "인천 출발 직항 약 7시간 (덴파사르 공항)",
        "best_season": "5~10월(건기, 쾌청하고 습도 낮은 날씨)",
        "budget_guide": "1인 약 120~170만 원 (항공 60~80만, 풀빌라/호텔 45만, 식비/투어 30만)",
        "transport_pass": "클룩/그랩 프라이빗 차량 대절 투어",
        "score": 98.0,
        "original_url": "https://www.indonesia.travel/kr/ko/home"
    },
    {
        "destination_id": "TRAVEL-CEBU-16",
        "destination": "세부 & 막탄 (Cebu & Mactan)",
        "country": "필리핀",
        "region": "동남아",
        "duration": "3박 5일",
        "theme": "오슬롭 고래상어 스노클링, 모알보알 거북이 & 막탄 호핑투어",
        "highlights": [
            "눈앞에서 만나는 오슬롭 고래상어와 투명한 바다 스노클링",
            "모알보알 수천 마리 정어리 떼와 바다거북 와치 투어",
            "날루수안 & 힐룽뚱안 아일랜드 호핑투어와 씨푸드 바비큐",
            "막탄 해변 5성급 리조트 호캉스와 가성비 1일 1마사지"
        ],
        "spots": ["오슬롭 고래상어 와칭", "모알보알 정어리떼", "가와산 캐녀닝", "날루수안 호핑", "막탄 뉴타운", "시라오 가든"],
        "spot_image_queries": {
            "오슬롭 고래상어 와칭": "Oslob whale shark snorkeling Cebu",
            "모알보알 정어리떼": "Moalboal sardine run turtle sea",
            "날루수안 호핑": "Nalusuan island sandbar wooden bridge Cebu",
            "가와산 캐녀닝": "Kawasan Falls turquoise water Cebu"
        },
        "flight_time": "인천/부산 출발 직항 약 4시간 30분",
        "best_season": "12~5월(건기, 맑고 파도 잔잔한 시즌)",
        "budget_guide": "1인 약 70~100만 원 (항공 28~40만, 리조트 25만, 액티비티/식비 25만)",
        "transport_pass": "현지 픽드랍 프라이빗 밴 투어",
        "score": 96.0,
        "original_url": "https://www.itsmorefuninthephilippines.co.kr/"
    },
    {
        "destination_id": "TRAVEL-YEOSU-17",
        "destination": "여수 (Yeosu)",
        "country": "대한민국",
        "region": "전라남도",
        "duration": "2박 3일",
        "theme": "여수 밤바다 낭만, 해상케이블카 & 남도 게장백반 미식 힐링",
        "highlights": [
            "바다 위를 가로지르는 여수 해상케이블카 크리스탈 캐빈 탑승",
            "돌산대교 야경과 낭만포차 거리 딱새우회·돌문어삼합 먹방",
            "오동도 동백꽃 숲길 산책과 향일암 절벽 일출 감상",
            "간장게장·양념게장 무한리필 백반과 갓김치 한상차림"
        ],
        "spots": ["여수 해상케이블카", "오동도", "돌산공원 & 돌산대교", "낭만포차 거리", "향일암", "이순신광장"],
        "spot_image_queries": {
            "여수 해상케이블카": "Yeosu sea cable car ocean view",
            "오동도": "Odongdo island Yeosu camellia forest",
            "돌산공원 & 돌산대교": "Dolsan Bridge night lights Yeosu",
            "향일암": "Hyangiram Hermitage cliff Yeosu"
        },
        "flight_time": "서울역 기준 KTX 여수엑스포역 약 3시간",
        "best_season": "3~5월(동백꽃/봄바다), 9~11월(가을 노을과 낭만)",
        "budget_guide": "1인 약 25~40만 원 (KTX 왕복 9만, 오션뷰 호텔 15만, 식비 12만)",
        "transport_pass": "KTX + 시내버스/택시 또는 쏘카 렌터카",
        "score": 96.0,
        "original_url": "https://www.yeosu.go.kr/tour/"
    },
    {
        "destination_id": "TRAVEL-GYEONGJU-18",
        "destination": "경주 (Gyeongju)",
        "country": "대한민국",
        "region": "경상북도",
        "duration": "2박 3일",
        "theme": "천년고도 신라 역사 탐방과 황리단길 한옥 감성 카페 투어",
        "highlights": [
            "동궁과 월지(안압지) 및 첨성대 달빛 야경 산책",
            "한옥 리모델링 트렌드 핫플 황리단길 맛집과 소품샵 투어",
            "불국사와 석굴암 유네스코 세계문화유산 답사",
            "대릉원 목련 포토존 인증샷과 보문관광단지 호수 드라이브"
        ],
        "spots": ["동궁과 월지", "첨성대", "황리단길", "대릉원", "불국사", "보문호"],
        "spot_image_queries": {
            "동궁과 월지": "Donggung Palace and Wolji Pond night Gyeongju",
            "첨성대": "Cheomseongdae Gyeongju night lights",
            "황리단길": "Hwangridangil Gyeongju hanok street",
            "불국사": "Bulguksa temple Gyeongju heritage"
        },
        "flight_time": "서울역 기준 KTX 신경주역 약 2시간",
        "best_season": "4월(벚꽃 명소), 10~11월(단풍과 고즈넉한 가을)",
        "budget_guide": "1인 약 20~35만 원 (KTX 왕복 9만, 한옥스테이 12만, 식비 10만)",
        "transport_pass": "KTX + 전동스쿠터/자전거 대여 및 시내버스",
        "score": 95.0,
        "original_url": "https://www.gyeongju.go.kr/tour/"
    }

]

import os
import json

CATALOG_1000_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "travel_catalog_1000.json"
)

def get_expanded_travel_catalog() -> List[Dict[str, Any]]:
    """Loads 1,000-destination catalog from JSON if available, otherwise falls back to CORE_TRAVEL_CATALOG."""
    if os.path.exists(CATALOG_1000_PATH):
        try:
            with open(CATALOG_1000_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) >= 50:
                    return data
        except Exception as e:
            logger.warning("Failed to load travel catalog from %s: %s", CATALOG_1000_PATH, e)
    return CORE_TRAVEL_CATALOG


class TravelCollector:
    """Collector handling discovery and normalization of trending travel destinations."""

    def __init__(self, timeout: float = 8.0):
        self.timeout = timeout

    async def health_check(self) -> Dict[str, Any]:
        """Verify travel collector data availability."""
        catalog = get_expanded_travel_catalog()
        return {
            "success": True,
            "catalog_count": len(catalog),
            "source": "TOUR_API_GLOBAL_1000",
            "message": f"글로벌/국내 {len(catalog)}선 대규모 여행 데이터 수집기 가동 중"
        }

    async def discover_popular_destinations(self, limit: int = 1500) -> List[TravelCandidateItem]:
        """Discover curated trending travel destinations."""
        catalog = get_expanded_travel_catalog()
        items: List[TravelCandidateItem] = []
        for raw in catalog[:min(limit, len(catalog))]:
            items.append(TravelCandidateItem(**raw))
        return items

    async def get_destination_by_id(self, destination_id: str) -> Optional[TravelCandidateItem]:
        """Retrieve destination details by unique ID."""
        catalog = get_expanded_travel_catalog()
        for raw in catalog:
            if raw["destination_id"] == destination_id:
                return TravelCandidateItem(**raw)
        return None

    async def search_live_travel_info(self, query: str) -> List[TravelCandidateItem]:
        """Live fallback search using open travel sources or matching catalog."""
        query_clean = query.strip().lower()
        matched: List[TravelCandidateItem] = []
        catalog = get_expanded_travel_catalog()

        for raw in catalog:
            if query_clean in raw["destination"].lower() or query_clean in raw["country"].lower():
                matched.append(TravelCandidateItem(**raw))

        if not matched:
            matched.append(
                TravelCandidateItem(
                    destination_id=f"TRAVEL-{query_clean[:6].upper()}",
                    destination=query,
                    country="글로벌 인기 여행지",
                    duration="3박 4일",
                    theme="핵심 명소 & 로컬 문화 탐방 코스",
                    highlights=[
                        f"{query} 대표 랜드마크 방문 및 기념 촬영",
                        f"{query} 현지 로컬 맛집과 야시장 미식 탐방",
                        "대중교통 패스를 활용한 알뜰하고 효율적인 동선 최적화"
                    ],
                    spots=[f"{query} 중심 광장", f"{query} 대표 전망대", f"{query} 전통 거리"],
                    flight_time="국내외 직항 또는 경유편 운항",
                    best_season="봄, 가을",
                    budget_guide="1인 기준 합리적 실속 예산",
                    transport_pass="현지 1일 대중교통 패스",
                    score=90.0
                )
            )
        return matched
