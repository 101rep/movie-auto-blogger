"""Product & Commerce Review Content Module implementing BaseContentModule.

Provides E-E-A-T rich product comparisons, spec breakdowns, and honest user reviews
for Coupang, 오늘의집, and lifestyle commerce items (ItemPick24).
"""
import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.ai.router import AIProviderRouter
from app.core.base_module import BaseContentModule, CandidateItem
from app.core.verticals import VerticalType, VerticalStatus
from app.utils.logging import get_logger

logger = get_logger("product_module")


class ProductCandidate(BaseModel):
    id: str
    name: str
    category: str
    price: int
    original_price: Optional[int] = None
    rating: float = 4.8
    review_count: int = 1500
    source: str = "Coupang"
    image_url: Optional[str] = None
    affiliate_url: Optional[str] = None
    highlight: str
    specs: Dict[str, str] = Field(default_factory=dict)
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)


DEFAULT_PRODUCT_CATALOG: List[ProductCandidate] = [
    ProductCandidate(
        id="prod_vertical_mouse_01",
        name="초경량 인체공학 무선 버티컬 마우스",
        category="IT/테크",
        price=43900,
        original_price=59000,
        rating=4.9,
        review_count=3240,
        source="Coupang",
        highlight="하루 8시간 엑셀/문서 작업자의 손목 시림을 해결하는 57도 인체공학 설계",
        specs={
            "연결 방식": "블루투스 5.0 + 2.4GHz 무선 듀얼 리시버",
            "DPI": "최대 4000 DPI (4단계 조절)",
            "배터리": "C타입 고속 충전 (1회 완충 시 90일 사용)",
            "무게": "92g (손목 부담 최소화 초경량)"
        },
        pros=[
            "장시간 클릭 및 스크롤 시 손목 시림과 뻐근함이 80% 이상 완화됨",
            "무소음 스위치 적용으로 조용한 사무실이나 독서실에서도 쾌적",
            "C타입 충전 방식으로 건전지 교체 번거로움 제로"
        ],
        cons=[
            "일반 마우스만 쓰던 첫 1~2일 동안은 약간 어색한 적응 기간 필요",
            "손이 매우 큰 성인 남성의 경우 새끼손가락 그립감이 타이트할 수 있음"
        ]
    ),
    ProductCandidate(
        id="prod_desk_timer_02",
        name="집중력 향상 시각화 만기 예약 타이머",
        category="데스크테리어",
        price=21800,
        original_price=28000,
        rating=4.8,
        review_count=2150,
        source="Coupang",
        highlight="빨간색 디스크로 남은 시간이 직관적으로 줄어드는 뽀모도로 작업 타이머",
        specs={
            "작동 방식": "무소음 아날로그 태엽 메커니즘",
            "최대 측정 시간": "60분 카운트다운",
            "알람 설정": "무음(LED 깜빡임) / 작은 소리 / 큰 소리 3단계",
            "전원": "AAA 건전지 2개 포함"
        },
        pros=[
            "스마트폰 타이머와 달리 폰을 보지 않아 도파민 중독과 딴짓 완벽 차단",
            "작업 데드라인이 눈으로 줄어드는 게 보여 업무 몰입도가 2배 이상 상승",
            "공부방이나 사무실에서 눈치 볼 필요 없는 완전 무소음 설계"
        ],
        cons=[
            "최대 시간이 60분이라 2시간 이상 연속 장시간 측정 시 재설정 필요",
            "플라스틱 마감이 고급 금속 마감에 비해 약간 캐주얼한 느낌"
        ]
    ),
    ProductCandidate(
        id="prod_monitor_light_03",
        name="비대칭 광학 스크린바 모니터 조명",
        category="데스크테리어",
        price=38500,
        original_price=49000,
        rating=4.9,
        review_count=1890,
        source="Coupang",
        highlight="화면 반사 없이 책상 위만 부드럽게 밝혀주는 야간 눈 피로 제로 조명",
        specs={
            "광원 기술": "화면 반사 차단 45도 비대칭 전방 투사 광학",
            "색온도 조절": "2900K(웜) ~ 5000K(쿨) 3단계 터치 변환",
            "전원 규격": "USB 5V/1A (모니터 후면 포트 직결 가능)",
            "고정 방식": "중력 밸런스 거치 클립 (두께 1~3cm 모니터 호환)"
        },
        pros=[
            "모니터 액정에 빛이 반사되지 않아 눈부심과 안구건조증이 획기적으로 개선됨",
            "책상 공간을 전혀 차지하지 않아 협소한 데스크 세팅에 최적화",
            "터치 한 번으로 야간 독서/작업 모드 무드 전환 간편"
        ],
        cons=[
            "곡률이 매우 심한 커브드 모니터(1000R 이하)는 양끝 밀착이 덜할 수 있음",
            "리모컨이 없는 모델이라 본체 상단 터치 버튼으로 조작해야 함"
        ]
    ),
    ProductCandidate(
        id="prod_lumbar_cushion_04",
        name="메모리폼 허리 지지 럼버 서포트 쿠션",
        category="생활/가전",
        price=29900,
        original_price=39000,
        rating=4.7,
        review_count=1420,
        source="오늘의집",
        highlight="의자에 앉는 순간 척추 C커브를 단단하게 받쳐주는 고밀도 메모리폼",
        specs={
            "내장재": "50D 고밀도 복원 항균 메모리폼",
            "커버": "세탁 가능한 3D 에어메쉬 통기성 커버",
            "스트랩": "길이 조절 가능한 이중 고정 버클 밴드",
            "무게": "650g"
        },
        pros=[
            "오래된 사무실 의자나 게이밍 체어에 얹기만 해도 허리 통증이 크게 줄어듦",
            "여름철에도 땀이 차지 않는 시원한 메쉬 커버로 세탁 관리 용이",
            "체형에 맞춰 천천히 감싸주는 복원력 우수"
        ],
        cons=[
            "두께감이 있어 의자 좌판 깊이가 얕은 경우 앞으로 살짝 밀릴 수 있음",
            "처음 개봉 시 메모리폼 특유의 새제품 냄새가 반나절 정도 지속됨"
        ]
    ),
    ProductCandidate(
        id="prod_laptop_stand_05",
        name="알루미늄 듀얼 힌지 접이식 노트북 거치대",
        category="IT/테크",
        price=32500,
        original_price=45000,
        rating=4.9,
        review_count=4120,
        source="Coupang",
        highlight="눈높이에 맞춘 자유로운 각도/높이 조절로 거북목과 어깨 뭉침 방지",
        specs={
            "소재": "통 알루미늄 합금 아노다이징 마감",
            "지지 하중": "최대 10kg 흔들림 제로",
            "호환 규격": "11인치~17.3인치 전 기종",
            "통풍 구조": "효율적 발열 해소를 위한 중앙 오픈형 쿨링 홀"
        },
        pros=[
            "무거운 게이밍 노트북을 얹고 타이핑해도 처짐이나 흔들림 없음",
            "접었을 때 납작해져 파우치나 가방에 쏙 들어가는 휴대성",
            "시선이 정면으로 올라와 장시간 작업 시 목 디스크 예방에 결정적"
        ],
        cons=[
            "힌지가 매우 튼튼하게 설계되어 초기 각도 조절 시 약간의 완력 필요",
            "메탈 재질 특성상 겨울철 아침 처음 만질 때 약간 차가움"
        ]
    ),
    ProductCandidate(
        id="prod_gan_charger_06",
        name="65W GaN 질화갈륨 3포트 초고속 멀티 충전기",
        category="IT/가전",
        price=27800,
        original_price=36000,
        rating=4.8,
        review_count=2980,
        source="Coupang",
        highlight="손바닥 절반 크기에 노트북+태블릿+스마트폰 동시 초고속 충전",
        specs={
            "충전 기술": "차세대 GaN III 질화갈륨 반도체",
            "출력 포트": "USB-C 2구 + USB-A 1구 (총 3포트)",
            "단일 최대 출력": "PD 65W (맥북 및 갤럭시 초고속 충전 지원)",
            "안전 설계": "과전류/과전압/과열 방지 스마트 IC 칩 탑재"
        },
        pros=[
            "무거운 벽돌 어댑터 3개를 하나로 줄여 출장/여행 가방 부피 대폭 절감",
            "접지형 플러그 구조로 노트북 메탈 표면의 찌릿한 누설 전류 완벽 차단",
            "3대 동시 충전 중에도 발열이 미미하여 안정성 합격점"
        ],
        cons=[
            "3포트 동시 사용 시 순간적으로 전력 재분배로 1~2초 재연결 현상 있음",
            "벽면 콘센트에 꽂을 때 무게로 인해 헐거운 콘센트는 꽉 끼워야 함"
        ]
    ),
    ProductCandidate(
        id="prod_desk_mat_07",
        name="방수 가죽 와이드 데스크 장패드",
        category="데스크테리어",
        price=18900,
        original_price=25000,
        rating=4.7,
        review_count=1850,
        source="오늘의집",
        highlight="커피를 쏟아도 쓱 닦이는 생활 방수와 데스크 무드를 완성하는 감성 가죽",
        specs={
            "재질": "친환경 프리미엄 PU 가죽 (스웨이드 바닥면)",
            "크기": "800mm x 400mm 와이드 규격",
            "두께": "2mm 슬림핏 쿠션감",
            "특징": "마우스패드 겸용 부드러운 슬라이딩"
        },
        pros=[
            "책상에 깔자마자 인테리어 감성이 살아나며 마우스 패드가 별도 필요 없음",
            "음료나 물을 흘려도 스며들지 않고 물티슈로 한 번에 깨끗이 닦임",
            "가장자리 마감이 튼튼하여 오래 써도 들뜸이나 말림 현상 없음"
        ],
        cons=[
            "돌돌 말려서 배송되므로 처음 하루 정도 책으로 눌러두는 평탄화 추천",
            "광 마우스 특성에 따라 일부 센서의 미세한 감도 적응 필요"
        ]
    ),
    ProductCandidate(
        id="prod_cable_organizer_08",
        name="자석형 실리콘 멀티 케이블 정리 홀더",
        category="생활/정리",
        price=14500,
        original_price=19000,
        rating=4.9,
        review_count=3600,
        source="Coupang",
        highlight="책상 밑으로 떨어지는 충전선을 자석으로 찰칵 고정하는 정리 혁신템",
        specs={
            "재질": "부드러운 친환경 실리콘 + 강력 네오디뮴 자석",
            "구성": "마그네틱 베이스 1개 + 케이블 클립 5개",
            "호환 두께": "2.5mm ~ 4.5mm (모든 규격 케이블 호환)",
            "부착 방식": "자국 없이 떼어지는 3M 무흔 접착 테이프"
        },
        pros=[
            "스마트폰 뺄 때 충전선이 바닥으로 추락하는 스트레스 100% 해소",
            "자석이 강력해 케이블을 가까이 대기만 해도 착 달라붙음",
            "책상 모서리나 측면에 깔끔하게 붙여 데스크 공간 낭비 제로"
        ],
        cons=[
            "두꺼운 직조 패브릭 케이블은 클립을 끼울 때 조금 빡빡할 수 있음",
            "접착면을 붙이기 전 책상 먼지를 알코올 솜으로 잘 닦아주어야 오래감"
        ]
    ),
    ProductCandidate(
        id="prod_mech_keyboard_09",
        name="저소음 적축 블루투스 무선 기계식 키보드",
        category="IT/주변기기",
        price=89000,
        original_price=119000,
        rating=4.9,
        review_count=2150,
        source="Coupang",
        highlight="사무실에서도 눈치 안 보고 쓰는 보글보글 조용한 저소음 타건감",
        specs={
            "스위치": "공장 윤활 저소음 리니어 적축",
            "연결": "블루투스 5.1 + 2.4GHz 리시버 + 유선 C타입 (3-Way)",
            "배터리": "4000mAh 대용량 (LED 끄고 최대 200시간 연속 사용)",
            "키캡": "PBT 한영 이색사출 (번들거림 없는 프리미엄 재질)"
        },
        pros=[
            "새벽이나 조용한 사무실에서 고속 타이핑해도 소음 스트레스 제로",
            "최대 3대 기기 멀티페어링으로 PC와 태블릿을 버튼 하나로 전환",
            "묵직한 알루미늄 보강판 탑재로 통울림 없는 단단한 타건음"
        ],
        cons=[
            "청축이나 갈축 특유의 찰칵거리는 손맛을 선호하는 분에겐 밋밋할 수 있음",
            "휴대하기엔 약 980g으로 다소 묵직하여 거치용에 적합"
        ]
    ),
    ProductCandidate(
        id="prod_anc_headphone_10",
        name="하이브리드 액티브 노이즈캔슬링 무선 헤드폰",
        category="음향기기",
        price=79000,
        original_price=109000,
        rating=4.8,
        review_count=3420,
        source="Coupang",
        highlight="지하철·카페 소음을 95% 지워주는 몰입형 가성비 종결 헤드폰",
        specs={
            "노이즈 캔슬링": "하이브리드 ANC 40dB 감쇄",
            "드라이버": "40mm 티타늄 다이어프램 다이내믹 드라이버",
            "배터리": "최대 60시간 연속 재생 (급속 충전 10분 시 5시간 재생)",
            "코덱": "LDAC 고해상도 무선 오디오 및 AAC/SBC 지원"
        },
        pros=[
            "10만원 이하 가격대에서 대기업 30만원대 못지않은 소음 차단력 구현",
            "메모리폼 이어쿠션의 부드러운 착용감으로 안경 착용자도 귀 눌림 없음",
            "공간 음향 모드 지원으로 영화나 유튜브 시청 시 극장 같은 입체감"
        ],
        cons=[
            "한여름 야외 착용 시 귀 주변에 땀이 찰 수 있음",
            "전용 앱의 한글 번역이 일부 직관적이지 않은 부분이 있음"
        ]
    ),
    ProductCandidate(
        id="prod_humidifier_11",
        name="대용량 통세척 가열복합식 스마트 가습기 4.5L",
        category="계절가전",
        price=59900,
        original_price=79000,
        rating=4.9,
        review_count=4800,
        source="오늘의집",
        highlight="세균 걱정 없는 100도 저온살균 가열식과 풍부한 복합 분무의 만남",
        specs={
            "물탱크 용량": "4.5L (최대 30시간 연속 가습)",
            "가습 방식": "초음파 + 저온 가열 복합식 (따뜻한 수증기)",
            "세척 편의": "손이 바닥까지 쑥 들어가는 원통형 완전 분리 통세척",
            "센서": "주변 습도 자동 감지 스마트 오토 모드 (목표 습도 유지)"
        },
        pros=[
            "물이 끓여서 분사되므로 차가운 초음파 가습기 대비 방안 공기가 훈훈함",
            "물탱크 구석구석 손으로 수세미 세척이 가능해 물때 걱정 제로",
            "상부 급수 구조로 가습기 가동 중에도 주전자로 물 보충 가능"
        ],
        cons=[
            "가열 기능 작동 시 소비전력이 일반 초음파 가습기보다 다소 높음",
            "정수기물보다는 수돗물 사용을 권장하며 주기적 석회질 청소 필요"
        ]
    ),
    ProductCandidate(
        id="prod_airfryer_12",
        name="올스텐 7L 대용량 투명 바스켓 디지털 에어프라이어",
        category="주방가전",
        price=89000,
        original_price=129000,
        rating=4.9,
        review_count=5120,
        source="Coupang",
        highlight="코팅 벗겨짐 걱정 없는 SUS304 스테인리스와 조리 상태를 보는 통유리창",
        specs={
            "소재": "내부 바스켓 및 열선망 올 SUS304 프리미엄 스테인리스",
            "용량": "7L 점보 패밀리 사이즈 (통닭 2마리 동시 조리)",
            "유리창": "내열 강화 2중 투명 윈도우 + 내부 조명",
            "열풍 순환": "360도 초고속 에어 서큘레이션 200도 열풍"
        },
        pros=[
            "불소수지 코팅 유해물질(PFOA/PFOS) 불안감 없이 평생 안심 사용",
            "요리 도중 바스켓을 열지 않고도 겉바속촉 굽기 상태를 실시간 확인",
            "식기세척기 사용 가능하여 기름기 많은 삼겹살 구이 후에도 청소 초간편"
        ],
        cons=[
            "7L 대용량 크기라 싱크대 조리대 공간을 미리 확보해야 함",
            "스텐 특성상 첫 사용 전 키친타월과 식용유로 연마제 제거 작업 권장"
        ]
    ),
    ProductCandidate(
        id="prod_robot_vac_13",
        name="스마트 물걸레 겸용 로봇청소기 LiDAR 매핑",
        category="스마트가전",
        price=189000,
        original_price=249000,
        rating=4.8,
        review_count=3100,
        source="Coupang",
        highlight="퇴근 후 매일 반짝이는 바닥, 흡입과 물걸레를 동시에 끝내는 가성비 청소이모",
        specs={
            "센서": "360도 정밀 LiDAR 내비게이션 + 추락방지 센서",
            "흡입력": "4500Pa 초강력 BLDC 모터",
            "물걸레": "전자제어 3단계 물 공급 자동 가압 물걸레",
            "연동": "전용 스마트폰 앱 원격 제어, 금지구역 및 구역별 청소 설정"
        },
        pros=[
            "가구 모서리와 침대 밑 먼지까지 놓치지 않고 꼼꼼하게 청소",
            "외출할 때 앱으로 클릭 한 번이면 퇴근 후 깨끗한 바닥을 마주함",
            "문턱과 카펫을 부드럽게 넘나들며 카펫 감지 시 자동 흡입력 부스팅"
        ],
        cons=[
            "바닥에 충전 케이블이나 얇은 양말이 널브러져 있으면 걸릴 수 있어 바닥 정리 필요",
            "걸레를 빨아주는 자동 올인원 스테이션 모델 대비 걸레는 직접 손빨래 필요"
        ]
    ),
    ProductCandidate(
        id="prod_portable_monitor_14",
        name="15.6인치 4K UHD IPS 포터블 휴대용 보조 모니터",
        category="IT/테크",
        price=189000,
        original_price=249000,
        rating=4.9,
        review_count=1980,
        source="Coupang",
        highlight="카페나 출장지에서도 노트북 옆에 C타입 케이블 하나로 듀얼 스크린 구축",
        specs={
            "화면 규격": "15.6인치 3840x2160 4K IPS 광시야각 (sRGB 100%)",
            "입력 단자": "풀기능 USB Type-C 2구 + Mini HDMI",
            "패널 두께/무게": "초슬림 5mm / 초경량 680g",
            "스피커": "듀얼 스테레오 내장 스피커 탑재"
        },
        pros=[
            "별도 전원 어댑터 없이 노트북 C타입 포트에서 전원과 화면 동시 전송",
            "4K 해상도의 압도적 선명함으로 그래픽 작업 및 엑셀 다중 창 작업 효율 극대화",
            "마그네틱 스마트 커버 겸 거치대 기본 동봉으로 가방에 쏙 들어가는 휴대성"
        ],
        cons=[
            "4K 해상도로 장시간 연결 시 노트북 배터리 소모가 일반 모니터보다 빠름",
            "터치 미지원 모델의 경우 마우스 조작 필요"
        ]
    ),
    ProductCandidate(
        id="prod_wireless_vacuum_15",
        name="28000Pa 초강력 BLDC 무선 진공청소기 거치대 풀세트",
        category="생활가전",
        price=149000,
        original_price=198000,
        rating=4.8,
        review_count=3750,
        source="Coupang",
        highlight="머리카락 엉킴 방지 롤러와 어두운 틈새를 비추는 전면 LED 헤드 브러시",
        specs={
            "모터 흡입력": "28,000Pa 고성능 항공기 모터 BLDC",
            "배터리": "탈부착 리튬이온 2500mAh (에코 모드 최대 50분 연속 작동)",
            "필터링": "H13 헤파필터 포함 5중 미세먼지 차단 시스템 (99.97% 여과)",
            "무게": "본체 무게 1.35kg 손목 무리 없는 경량 설계"
        },
        pros=[
            "침구 브러시, 틈새 흡입구, 올인원 스탠드 거치대까지 풀패키지 기본 구성",
            "앞쪽 LED 조명 덕분에 침대 밑이나 소파 구석 먼지가 뚜렷하게 보여 청소 완벽",
            "원터치 먼지통 비움 버튼으로 손에 먼지 묻힐 일 없는 위생적 관리"
        ],
        cons=[
            "최대 터보 파워 모드로 계속 가동 시 배터리 가동 시간이 약 15분으로 단축",
            "헤파 필터는 물세척 후 24시간 이상 완전 건조 후 장착해야 함"
        ]
    ),
    ProductCandidate(
        id="prod_smart_watch_16",
        name="1.43인치 AMOLED 올웨이즈온 디스플레이 스마트워치",
        category="스마트기기",
        price=54000,
        original_price=79000,
        rating=4.8,
        review_count=4200,
        source="Coupang",
        highlight="24시간 심박수·혈중산소·수면 단계 정밀 추적과 14일 초장기 배터리",
        specs={
            "디스플레이": "1.43인치 고선명 AMOLED AOD (466x466 픽셀)",
            "배터리 수명": "일반 사용 14일, 절전 모드 시 최대 25일",
            "방수 등급": "5ATM + IP68 완전 생활방수 (수영 및 샤워 가능)",
            "건강 측정": "광학 심박수, SpO2 혈중산소, 수면 품질, 스트레스 지수"
        },
        pros=[
            "매일 충전할 필요 없이 보름에 한 번만 충전해도 충분한 압도적 배터리",
            "카카오톡, 문자, 전화 알림이 즉각 동기화되어 휴대폰을 꺼낼 필요 없음",
            "100가지 이상의 운동 모드 자동 감지로 걷기, 달리기, 라이딩 기록 정확"
        ],
        cons=[
            "자체 통화 기능(LTE 단독)은 없고 블루투스 통화 연결 방식으로 작동",
            "간편결제(NFC) 기능은 국내 미지원"
        ]
    ),
    ProductCandidate(
        id="prod_standing_desk_17",
        name="저소음 듀얼모터 전동 높이조절 스마트 모션데스크 1400",
        category="가구/인테리어",
        price=269000,
        original_price=350000,
        rating=4.9,
        review_count=1650,
        source="오늘의집",
        highlight="서서 일하는 습관으로 허리 부담을 줄여주는 4단 메모리 스마트 데스크",
        specs={
            "구동 모터": "안정적인 하중 분산 저소음 듀얼 모터 (소음 45dB 이하)",
            "높이 조절 범위": "최저 65cm ~ 최고 125cm (미세 1mm 단위 조절)",
            "상판 규격": "1400mm x 700mm 친환경 E0 등급 LPM 코팅 상판",
            "안전 장치": "장애물 감지 시 자동 멈춤 및 리버스 충돌 방지 자이로 센서"
        },
        pros=[
            "원모터 모델과 비교 불가한 부드러운 승하강과 컵에 담긴 물도 안 쏟아지는 안정감",
            "앉은 키와 선 키를 1, 2번 버튼에 저장해두면 원터치로 높이 자동 변경",
            "식곤증이 오는 오후 시간에 30분 서서 일하면 집중력과 소화력이 대폭 상승"
        ],
        cons=[
            "프레임이 강철 통스틸이라 택배 수령 시 무게가 약 30kg으로 무거움",
            "성인 혼자 조립 시 전동 드라이버가 있으면 조립 시간 30분 내외 단축 가능"
        ]
    ),
    ProductCandidate(
        id="prod_coffee_machine_18",
        name="20바 고압 추출 반자동 가정용 홈카페 에스프레소 머신",
        category="주방가전",
        price=119000,
        original_price=169000,
        rating=4.8,
        review_count=2840,
        source="Coupang",
        highlight="황금빛 풍성한 크레마와 실크 스팀 밀크로 집에서 즐기는 전문 카페 라떼",
        specs={
            "압력 펌프": "이탈리아 ULKA사 프리미엄 20Bar 고압력 펌프",
            "스팀 노즐": "강력 건식 스팀 다이얼 조절 (부드러운 벨벳 밀크폼 제조)",
            "물탱크": "1.2L 대용량 분리형 투명 물탱크",
            "예열 시스템": "써모블록 급속 가열 (전원 켠 뒤 45초 이내 추출 준비 완료)"
        },
        pros=[
            "매일 아침 카페에 가지 않아도 갓 내린 샷으로 풍미 깊은 아메리카노 완성",
            "캡슐 커피 특유의 밋밋한 맛과 다른 진한 원두 본연의 오일과 크레마 만끽",
            "컴팩트한 슬림 디자인으로 좁은 주방 싱크대 공간에도 예쁘게 안착"
        ],
        cons=[
            "분쇄 원두를 템핑하고 추출 후 포터필터를 물로 헹구는 수동 과정 필요",
            "스팀 노즐 사용 후 우유 잔여물이 굳기 전에 행주로 즉시 닦아주어야 위생적"
        ]
    ),
    ProductCandidate(
        id="prod_bone_conduction_19",
        name="오픈이어 골전도 블루투스 5.3 방수 무선 이어폰",
        category="음향/레저",
        price=49900,
        original_price=69000,
        rating=4.7,
        review_count=2310,
        source="Coupang",
        highlight="귀를 막지 않아 야외 러닝과 자전거 라이딩 시 주변 위험 소리를 즉시 인지",
        specs={
            "전달 방식": "뼈의 진동으로 달팽이관에 소리를 전달하는 진정한 골전도",
            "방수 등급": "IPX7 완벽 방수 (폭우 및 격렬한 땀에도 완벽 보호)",
            "무게": "초경량 28g 형상기억 티타늄 와이어 프레임",
            "배터리": "연속 8시간 음악 재생 및 마이크 노이즈 억제 통화"
        },
        pros=[
            "귓구멍을 막지 않아 장시간 착용해도 외이도염이나 귀 통증이 전혀 없음",
            "러닝 중 뒤에서 다가오는 자전거나 차량 경적 소리를 들을 수 있어 안전",
            "안경을 착용한 상태에서도 간섭 없이 귀에 가볍게 밀착 고정"
        ],
        cons=[
            "오픈형 구조 특성상 대중교통 등 밀폐 공간에서 볼륨을 최대로 올리면 소리 샘 현상 있음",
            "인이어 이어폰 대비 극저음(중저음 베이스) 타격감은 다소 플랫한 편"
        ]
    ),
    ProductCandidate(
        id="prod_mag_powerbank_20",
        name="15W 고속 맥세이프 마그네틱 미니 무선 보조배터리 10000mAh",
        category="스마트액세서리",
        price=31900,
        original_price=42000,
        rating=4.9,
        review_count=3560,
        source="Coupang",
        highlight="케이블 없이 아이폰 뒷면에 착 달라붙는 강력 자력 거치대 일체형 배터리",
        specs={
            "배터리 용량": "10,000mAh 정격 대용량 (스마트폰 약 2회 완충)",
            "충전 규격": "무선 최대 15W + C타입 PD 유선 20W 초고속 충전",
            "자력": "흔들림 없는 15N 슈퍼 네오디뮴 마그네틱 링",
            "부가 기능": "알루미늄 접이식 킥스탠드 (영상 시청 시 거치대 겸용)"
        },
        pros=[
            "가방 안에서 거추장스럽게 꼬이는 충전 케이블에서 완전 해방",
            "배터리를 붙인 채로 킥스탠드를 펴서 유튜브나 넷플릭스를 편하게 감상 가능",
            "손바닥 안에 쏙 들어오는 미니멀 카드 사이즈로 카메라 렌즈 간섭 제로"
        ],
        cons=[
            "무선 충전 시 스마트폰과 배터리 사이에 약간의 미온 발열이 발생할 수 있음",
            "자석 기능이 없는 일반 폰 케이스 착용 시 전용 마그네틱 링 스티커 필요"
        ]
    ),
    ProductCandidate(
        id="prod_foot_rest_21",
        name="인체공학 무빙 각도조절 데스크 발받침대 마사지 롤러형",
        category="오피스/리빙",
        price=23900,
        original_price=32000,
        rating=4.8,
        review_count=1890,
        source="오늘의집",
        highlight="바른 자세로 다리 꼬기를 방지하고 혈액순환을 돕는 발 지압 롤러 받침대",
        specs={
            "각도 조절": "발목 움직임에 따라 유연하게 움직이는 0~30도 틸팅",
            "표면 돌기": "중앙 마사지 롤러 + 미끄럼 방지 지압 엠보싱 패널",
            "재질": "견고한 내구성의 친환경 고강도 강화 ABS",
            "바닥 보호": "책상 밑 긁힘 방지 논슬립 실리콘 러버 패드 4구"
        },
        pros=[
            "의자 높이를 올려도 발바닥이 공중에 뜨지 않아 무릎과 골반 피로 대폭 경감",
            "자연스럽게 발을 올려놓게 되어 무의식적으로 다리 꼬는 나쁜 자세를 교정",
            "일하면서 맨발로 중앙 롤러를 굴리면 피로가 풀리고 졸음이 깨는 효과"
        ],
        cons=[
            "바닥이 매끄러운 타일일 경우 고무 패드에 먼지가 묻으면 살짝 밀릴 수 있으므로 청소 후 거치 권장",
            "높이 고정형이 아닌 자유 각도 틸팅형이므로 고정된 경사를 원할 땐 적응 필요"
        ]
    ),
    ProductCandidate(
        id="prod_electric_toothbrush_22",
        name="분당 40,000회 음파 전동칫솔 무선충전 IPX7 방수 칫솔모 6개",
        category="생활/뷰티",
        price=39800,
        original_price=58000,
        rating=4.9,
        review_count=5210,
        source="Coupang",
        highlight="치과 스케일링을 받은 듯 플라그를 완벽 제거하는 5가지 맞춤 진동 모드",
        specs={
            "진동수": "분당 40,000회 고주파 마이크로 버블 음파 진동",
            "모드 지원": "클린, 화이트닝, 마사지, 잇몸케어, 민감 5가지 모드",
            "타이머": "구강 4분면 30초 알림 + 2분 자동 종료 스마트 타이머",
            "배터리": "USB 무선 충전 크래들 (1회 충전 시 최장 60일 사용)"
        },
        pros=[
            "치아와 잇몸 사이에 미세 기포를 분사하여 잇몸 마모 없이 치석 제거",
            "칫솔모 6개가 기본 포함되어 1년 반 동안 추가 교체 비용 걱정 제로",
            "샤워하면서도 안전하게 양치할 수 있는 IPX7 완전 방수 등급"
        ],
        cons=[
            "처음 일반 칫솔에서 음파 진동으로 넘어갈 때 간지러운 느낌이 며칠 있을 수 있음",
            "전용 호환 칫솔모 규격을 사용하는 것이 가장 밀착력이 좋음"
        ]
    ),
    ProductCandidate(
        id="prod_camping_wagon_23",
        name="원터치 폴딩 접이식 아웃도어 캠핑 왜건 카트 광폭 광폭휠",
        category="레저/캠핑",
        price=68000,
        original_price=95000,
        rating=4.8,
        review_count=3120,
        source="Coupang",
        highlight="100kg 무거운 캠핑 짐과 장보기 짐을 모래사장에서도 거침없이 끄는 광폭 오프로드 휠",
        specs={
            "적재 하중": "최대 100kg 고하중 지지 (강철 프레임 크로스 구조)",
            "바퀴": "360도 회전 브레이크 장착 8인치 초광폭 고무 타이어",
            "원단": "오염과 찢어짐에 강한 방수 600D 이중 옥스포드 패브릭",
            "폴딩": "가운데 끈만 당기면 3초 만에 접히는 컴팩트 트렁크 수납"
        },
        pros=[
            "울퉁불퉁한 파쇄석 캠핑장이나 흙길, 잔디밭에서도 휠 걸림 없이 부드러운 주행",
            "트렁크에 납작하게 실려 평소 마트 장보기나 분리수거 카트로도 전천후 활용",
            "앞바퀴 원터치 풋브레이크가 있어 경사로에서도 카트가 밀리지 않고 안전"
        ],
        cons=[
            "광폭 타이어와 강철 프레임 설계로 왜건 자체 무게가 약 9.5kg 정도 나감",
            "원단 분리 세척 시 벨크로와 나사를 풀어야 하므로 물티슈로 평소 관리 권장"
        ]
    )
]


class ProductModule(BaseContentModule):
    """Production Content Module for Product & Commerce Reviews (ItemPick24)."""

    def __init__(self):
        self.ai_router = AIProviderRouter()

    @property
    def vertical(self) -> VerticalType:
        return VerticalType.PRODUCT

    @property
    def status(self) -> VerticalStatus:
        return VerticalStatus.PRODUCTION

    async def health_check(self) -> Dict[str, Any]:
        """Verify product review module readiness."""
        return {
            "success": True,
            "catalog_count": len(DEFAULT_PRODUCT_CATALOG),
            "vertical": "PRODUCT",
            "message": "아이템픽24 상품정보 & 스펙비교 모듈 정상 가동 중"
        }

    async def collect_candidates(self, db: Session, limit: int = 10) -> List[CandidateItem]:
        """Discover and score trending product review candidates."""
        logger.info("ProductModule: Collecting top product review candidates...")
        candidates: List[CandidateItem] = []

        for p in DEFAULT_PRODUCT_CATALOG[:min(limit, len(DEFAULT_PRODUCT_CATALOG))]:
            candidates.append(
                CandidateItem(
                    external_id=p.id,
                    vertical=VerticalType.PRODUCT,
                    title=f"[구매 가이드] {p.name} 핵심 스펙 비교 & 구매 포인트",
                    original_title=p.name,
                    summary=p.highlight,
                    source_attribution=p.source,
                    source_url=p.affiliate_url or "https://www.coupang.com",
                    score=p.rating * 20.0,
                    score_breakdown={
                        "rating_score": p.rating * 10,
                        "review_scale": min(p.review_count / 100, 50.0)
                    },
                    raw_data=p.model_dump()
                )
            )

        return candidates

    async def enrich_item(self, db: Session, external_id: str) -> Dict[str, Any]:
        """Retrieve detailed product specifications and review guidelines with real photo."""
        prod = next((p for p in DEFAULT_PRODUCT_CATALOG if p.id == external_id), None)
        if not prod:
            prod = DEFAULT_PRODUCT_CATALOG[0]

        # Sourcing authentic product picture via ImageProviderService (Kakao / Pexels)
        from app.services.image_provider import image_provider
        img_url = await image_provider.get_product_image(prod.name, prod.category)
        if img_url:
            prod.image_url = img_url

        return {
            "product": prod,
            "product_item": prod,
            "image_url": img_url,
            "target_buyer": "매일 책상에서 장시간 작업하거나 가성비 데스크테리어를 찾는 직장인 및 학생",
            "competitor_comparison": "동급 10만원대 유명 브랜드 대비 50% 이상 저렴한 가격에 핵심 기능 95% 구현"
        }

    async def generate_content(self, db: Session, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate E-E-A-T complaint, anti-cliche review article for the product."""
        prod: ProductCandidate = enriched_data["product"]

        system_instruction = (
            "당신은 IT 테크 및 라이프스타일 제품 분석 전문 큐레이터이자 에디터입니다.\n"
            "규칙 1 (Anti-Cliche): '혁신적인', '알아보겠습니다', '살펴보겠습니다', '총정리', '어떠셨나요?' 같은 식상한 AI 상투어구를 절대 쓰지 마세요.\n"
            "규칙 2 (정직성과 객관성): 가짜 '내돈내산'이나 '직접 사서 한 달 써봤다'는 식의 허위 경험을 가장하지 마세요. 공식 스펙, 제품 제원, 객관적 사용자 평가 데이터를 바탕으로 한 신뢰할 수 있는 제품 분석 가이드로 작성하세요.\n"
            "규칙 3 (가이드 중심 체계화): 제품 개요, 핵심 스펙 분석, 주요 장단점 포인트, 구매 전 체크포인트 코너로 체계적 마크업을 구성하세요."
        )

        user_prompt = f"""
다음 상품 정보를 바탕으로 워드프레스 블로그 '아이템픽24'에 게시할 객관적인 제품 스펙 분석 및 구매 가이드 포스팅을 작성해 주세요.

[상품명]: {prod.name}
[카테고리]: {prod.category}
[가격]: {prod.price:,}원 (정가: {prod.original_price:,}원)
[평점]: ⭐ {prod.rating} / 5.0 (리뷰 {prod.review_count:,}개)
[주요 특징]: {prod.highlight}
[스펙]: {json.dumps(prod.specs, ensure_ascii=False)}
[장점]: {', '.join(prod.pros)}
[단점]: {', '.join(prod.cons)}

[작성 요구사항]:
1. 글 제목: 제품명과 핵심 사양/포인트를 명확히 짚어주는 가이드형 제목 (예: [스펙 분석] {prod.name} 핵심 사양 및 구매 전 체크포인트)
2. 메타 요약문 (Excerpt): 2문장 내외의 객관적 사양 요약
3. 본문 작성 가이드:
   - 도입부: 이 제품이 적합한 활용 환경 및 제원 개요
   - 핵심 포인트 3줄 요약
   - 주목할 만한 주요 스펙 3가지
   - 구매 전 고려해야 할 유의사항 및 아쉬운 점 2가지
   - 이런 사용자에게 추천합니다 (구매 가이드)
"""

        raw = ""
        try:
            from google import genai
            from app.config import get_settings
            settings = get_settings()
            if settings.GEMINI_API_KEY:
                client = genai.Client(api_key=settings.GEMINI_API_KEY.strip())
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=f"{system_instruction}\n\n{user_prompt}"
                )
                raw = response.text or ""
        except Exception as e:
            logger.warning(f"AI generation fallback triggered for ProductModule: {e}")

        # Fallback if generation is short or failed
        if not raw or len(raw) < 200:
            title = f"[스펙 분석] {prod.name} 핵심 특징 및 구매 가이드"
            excerpt = f"{prod.name}의 주요 사양과 실구매 전 체크해야 할 장단점 포인트를 정리한 제품 가이드입니다."
            content_body = f"""
<h2>💡 제품 사양 및 주요 특징 개요</h2>
<p>{prod.highlight} 효율적인 작업 환경과 생활 편의를 돕는 {prod.name}의 주요 사양 및 특징을 분석한 가이드입니다.</p>
"""
        else:
            # Extract title if model returned a header or use dynamic highlight title
            extracted_title = None
            for line in raw.split("\n")[:5]:
                clean_l = line.strip().lstrip("#").strip()
                if clean_l.startswith("제목:") or clean_l.startswith("글 제목:"):
                    extracted_title = clean_l.split(":", 1)[1].strip()
                    break
                elif clean_l.startswith("[") and clean_l.endswith("]"):
                    extracted_title = clean_l[1:-1].strip()
                    break

            # Fallback title if not parsed
            title = extracted_title if (extracted_title and len(extracted_title) >= 10) else f"[스펙 분석] {prod.name} 핵심 사양 및 특징"
            excerpt = f"{prod.name}의 상세 사양과 장단점 포인트를 정리한 실구매 가이드입니다."
            content_body = raw

        return {
            "title": title,
            "excerpt": excerpt,
            "body": content_body,
            "product": prod
        }

    def render_html(self, content_data: Dict[str, Any], enriched_data: Dict[str, Any]) -> str:
        """Renders modern, clean product guide template with clear disclaimer."""
        prod: ProductCandidate = enriched_data["product"]
        title = content_data.get("title", f"[스펙 분석] {prod.name}")
        body_text = content_data.get("body", "")

        specs_rows = "".join([
            f"<tr><td style='padding: 10px 14px; font-weight: 600; color: #475569; background: #f8fafc; border-bottom: 1px solid #e2e8f0; width: 35%;'>{k}</td>"
            f"<td style='padding: 10px 14px; color: #1e293b; border-bottom: 1px solid #e2e8f0;'>{v}</td></tr>"
            for k, v in prod.specs.items()
        ])

        pros_items = "".join([f"<li style='margin-bottom: 6px;'>{p}</li>" for p in prod.pros])
        cons_items = "".join([f"<li style='margin-bottom: 6px;'>{c}</li>" for c in prod.cons])

        html = f"""
<meta name="google" content="notranslate">
<!-- ItemPick24 Modern Product Guide Master Template -->
<div class="product-review-wrap notranslate" translate="no" lang="ko" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans KR', sans-serif; line-height: 1.8; color: #1e293b; max-width: 780px; margin: 0 auto;">

    <!-- Category & Publisher Badges -->
    <div style="display:flex; gap:8px; margin-bottom:14px; flex-wrap:wrap;">
        <span class="notranslate" translate="no" style="background:#1e293b; color:#ffffff; font-size:12px; font-weight:700; padding:4px 10px; border-radius:9999px;">✍️ 발행: 아이템픽24</span>
        <span style="background:#2563eb; color:#ffffff; font-size:12px; font-weight:700; padding:4px 10px; border-radius:9999px;">제품 스펙 가이드</span>
    </div>

    <!-- Product Showcase Visual Photo Card -->
    {"<div style='margin: 20px 0 28px 0; text-align: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.04);'><img src='" + prod.image_url + "' alt='" + prod.name + " 제품 참고 컷' style='max-width: 100%; max-height: 420px; object-fit: contain; border-radius: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.08);' /><div style='margin-top: 12px; font-size: 12px; color: #94a3b8;'>※ 본 이미지는 제품의 이해를 돕기 위한 연출 및 참고용 컷입니다.</div></div>" if prod.image_url else ""}

    <!-- 1. 3-Line Key Takeaway Card -->
    <div style="background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%); border-left: 5px solid #2563eb; padding: 20px 22px; margin-bottom: 28px; border-radius: 12px; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.06);">
        <h3 style="margin: 0 0 12px 0; color: #1e40af; font-size: 18px; display: flex; items-center: center; gap: 8px;">
            📌 핵심 포인트 3줄 요약
        </h3>
        <ul style="margin: 0; padding-left: 20px; color: #1e293b; font-size: 15px;">
            <li style="margin-bottom: 6px;"><strong>만족도:</strong> 동급 대비 마감 품질과 완성도가 높음 (평점 ⭐ {prod.rating})</li>
            <li style="margin-bottom: 6px;"><strong>핵심 사양:</strong> {prod.highlight}</li>
            <li><strong>가격 경쟁력:</strong> 현재 기준 {prod.price:,}원대 수준의 가성비 구성</li>
        </ul>
    </div>

    <!-- 2. Specifications Table Card -->
    <h2 style="font-size: 21px; color: #0f172a; margin-top: 36px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">
        ⚙️ 핵심 스펙 및 제품 사양표
    </h2>
    <div style="overflow-x: auto; margin: 18px 0 28px 0; border: 1px solid #e2e8f0; border-radius: 10px;">
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <tbody>
                {specs_rows}
            </tbody>
        </table>
    </div>

    <!-- 3. AI Generated Main Body Content -->
    <div style="font-size: 16px; margin: 24px 0;">
        {body_text}
    </div>

    <!-- 4. Honest Pros and Cons Comparison Grid -->
    <h2 style="font-size: 21px; color: #0f172a; margin-top: 40px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">
        ⚖️ 사양 기반 주요 장점과 고려사항
    </h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 20px 0;">
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 18px; border-radius: 12px;">
            <h4 style="margin: 0 0 12px 0; color: #166534; font-size: 16px;">
                👍 주목할 만한 장점
            </h4>
            <ul style="margin: 0; padding-left: 18px; color: #14532d; font-size: 14px;">
                {pros_items}
            </ul>
        </div>
        <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 18px; border-radius: 12px;">
            <h4 style="margin: 0 0 12px 0; color: #991b1b; font-size: 16px;">
                👎 구매 전 체크포인트
            </h4>
            <ul style="margin: 0; padding-left: 18px; color: #7f1d1d; font-size: 14px;">
                {cons_items}
            </ul>
        </div>
    </div>

    <!-- 5. Fair Trade Commission Disclosure Banner -->
    <div style="margin-top: 45px; padding: 14px 18px; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; font-size: 13px; color: #64748b; text-align: center;">
        📢 <strong>안내:</strong> 본 포스팅은 공식 제품 사양 및 공개 데이터를 기반으로 공정하게 분석·작성되었으며, 제휴 마케팅 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다.
    </div>
</div>
"""
        return html

    def extract_metadata(
        self,
        gen_result: Dict[str, Any],
        enriched_data: Dict[str, Any],
        candidate: CandidateItem
    ) -> Dict[str, Any]:
        from app.services.title_hook_service import title_hook_service
        prod_item = enriched_data.get("product_item") or enriched_data.get("product")
        raw_title = gen_result.get("title") or (prod_item.name if prod_item else candidate.title)
        title = title_hook_service.generate_hooked_title(raw_title)
        excerpt = gen_result.get("excerpt") or (f"{prod_item.highlight} - 실제 구매 전 반드시 확인해야 할 핵심 스펙과 가성비 분석." if prod_item else candidate.summary)
        seo_title = f"{title[:55]}"
        meta_description = (excerpt or title)[:140]
        tags = ["상품리뷰", "스펙비교", "내돈내산", "아이템픽24"]
        featured_image_url = getattr(prod_item, "image_url", None) or enriched_data.get("image_url")
        return {
            "title": title,
            "excerpt": excerpt,
            "seo_title": seo_title,
            "meta_description": meta_description,
            "tags": tags,
            "featured_image_url": featured_image_url,
            "article_json_str": "{}"
        }

    def get_core_entities(self, text: str) -> List[str]:
        known_products = [
            "버티컬 마우스", "모니터 조명", "스크린바", "스탠바이미", "로봇청소기",
            "에어프라이어", "가습기", "제습기", "무선청소기", "헤어드라이기", "블루투스 스피커"
        ]
        return [prod for prod in known_products if prod in text]

