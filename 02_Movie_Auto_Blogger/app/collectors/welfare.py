"""Collector for Korean Government Welfare & Benefit Programs (복지로, 정부24, 정책브리핑)."""
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET
import httpx
from pydantic import BaseModel, Field

from app.collectors.gov24_welfare import Gov24WelfareClient, gov24_welfare_client
from app.utils.logging import get_logger

logger = get_logger("welfare_collector")


class WelfareCandidateItem(BaseModel):
    """Normalized welfare program candidate."""
    service_id: str
    service_name: str
    category: str = "정부지원"
    target_summary: str
    benefit_summary: str
    benefit_highlight: str
    application_period: str = "연중 상시 접수"
    apply_url: str = "https://www.bokjiro.go.kr"
    inquiry_contact: str = "보건복지상담센터 (129)"
    competent_agency: str = "보건복지부"
    eligibility_checklist: List[str] = Field(default_factory=list)
    application_steps: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    caution_notes: List[str] = Field(default_factory=list)
    stats_fact_box: Optional[str] = None
    legal_basis: Optional[str] = None
    score: float = 85.0
    source_attribution: str = "대한민국 공공데이터포털(data.go.kr) & 정부24 (공공누리 제1유형)"


# Core curated repository of high-interest Korean Welfare Programs
CORE_WELFARE_CATALOG: List[Dict[str, Any]] = [
    {
        "service_id": "WELFARE-YOUTH-LEAP-01",
        "service_name": "청년도약계좌",
        "category": "청년 금융·자산형성",
        "target_summary": "만 19~34세 청년 중 개인소득 연 7,500만원 이하 및 가구소득 중위 250% 이하",
        "benefit_summary": "매월 최대 70만원 자유 납입 시 정부기여금(매월 최대 3.3만원) 매칭 지원 및 이자소득 비과세 혜택 (5년 만기 시 최대 약 5,000만원 목돈 마련)",
        "benefit_highlight": "5년 만기 시 정부기여금+이자 비과세로 최대 5,000만원 자산 형성",
        "application_period": "매월 초 지정 은행(KB국민, 신한, 우리, 하나, NH농협 등) 앱에서 신청",
        "apply_url": "https://www.kinfa.or.kr",
        "inquiry_contact": "서민금융진흥원 (1397)",
        "competent_agency": "금융위원회 / 서민금융진흥원",
        "eligibility_checklist": [
            "가입일 기준 만 19세 이상 34세 이하 청년 (병역 이행 시 최대 6년 연장 가능)",
            "직전 과세기간 총급여액 7,500만원 이하 (종합소득금액 6,300만원 이하)",
            "가구원 수에 따른 기준 중위소득 250% 이하 충족",
            "직전 3개년도 중 1회 이상 금융소득종합과세 대상자가 아닌 자"
        ],
        "application_steps": [
            "1단계: 취급 11개 시중은행 모바일 앱에서 청년도약계좌 가입 신청",
            "2단계: 서민금융진흥원에서 개인소득 및 가구소득 심사 진행 (약 2~3주)",
            "3단계: 심사 통과 알림톡 수신 후 신청 은행 앱에서 계좌 개설 완료"
        ],
        "required_documents": [
            "신분증 (주민등록증, 운전면허증, 모바일신분증)",
            "비대면 자동 스크래핑을 통한 소득금액증명원 및 주민등록등본 확인 (별도 서류 제출 불필요)"
        ],
        "caution_notes": [
            "청년희망적금 만기자는 청년도약계좌 일시납입 연계 가입이 가능합니다.",
            "중도 해지 시 정부기여금 지급 및 비과세 혜택이 취소될 수 있으니 신중히 계획해야 합니다."
        ],
        "score": 98.0
    },
    {
        "service_id": "WELFARE-JOB-SEEKER-02",
        "service_name": "국민취업지원제도",
        "category": "일자리·취업지원",
        "target_summary": "만 15~69세 구직자 중 소득 및 재산 요건 충족자 (I유형: 중위소득 60% 이하, 재산 4억원 이하 청년 특례 지원)",
        "benefit_summary": "I유형: 구직촉진수당 월 50만원씩 6개월(최대 300만원) + 부양가족 1인당 월 10만원 추가 지원 / II유형: 취업활동비용 및 직업훈련 연계",
        "benefit_highlight": "구직촉진수당 매월 50만원씩 6개월(최대 300만원)+맞춤 취업지원",
        "application_period": "연중 상시 온라인 및 고용복지플러스센터 방문 접수",
        "apply_url": "https://www.work24.go.kr",
        "inquiry_contact": "고용노동부 고객상담센터 (1350)",
        "competent_agency": "고용노동부",
        "eligibility_checklist": [
            "만 15세~69세 구직자 (청년은 18세~34세 특례 적용)",
            "가구 단위 기준 중위소득 60% 이하 및 재산 합계액 4억원 이하",
            "최근 2년 이내 100일 또는 800시간 이상의 취업경험 보유 (선발형은 취업경험 무관)"
        ],
        "application_steps": [
            "1단계: 고용24(work24.go.kr) 회원가입 및 구직신청 등록",
            "2단계: 취업지원 신청서 제출 및 소득/재산 자격 심사",
            "3단계: 1개월 이내 수급자격 결정 통지 및 전담 상담사와 취업활동계획(IAP) 수립",
            "4단계: 매월 구직활동 이행 보고 후 구직촉진수당 50만원 입금"
        ],
        "required_documents": [
            "취업지원 신청서 및 개인정보 수집·이용 동의서",
            "가족관계증명서 및 주민등록등본 (행정정보공동이용 동의 시 자동 확인)",
            "취업경험 증빙 서류 (근로계약서, 경력증명서 등)"
        ],
        "caution_notes": [
            "구직촉진수당 지급 주기 중 월 549,600원 초과 소득 발생 시 해당 회차 수당 미지급 처리됩니다.",
            "정당한 사유 없이 취업활동계획을 불이행할 경우 수당 지급이 중단됩니다."
        ],
        "score": 95.0
    },
    {
        "service_id": "WELFARE-YOUTH-RENT-03",
        "service_name": "청년월세 특별지원",
        "category": "주거지원",
        "target_summary": "만 19~34세 부모와 별도 거주하는 무주택 청년 중 청년가구 중위 60% 이하 & 원가구 중위 100% 이하",
        "benefit_summary": "실제 납부하는 월세 중 최대 20만원씩 최대 12개월(총 240만원) 분할 현금 지원",
        "benefit_highlight": "매월 최대 20만원씩 1년 동안 최대 240만원 월세 지원",
        "application_period": "복지로 온라인 신청 또는 주소지 관할 행정복지센터 방문 접수",
        "apply_url": "https://www.bokjiro.go.kr",
        "inquiry_contact": "국토교통부 콜센터 (1600-0777)",
        "competent_agency": "국토교통부",
        "eligibility_checklist": [
            "신청일 기준 만 19세 이상 34세 이하 무주택 청년",
            "임차보증금 5천만원 이하 및 월세 70만원 이하 주택 거주",
            "청년 독립가구 소득평가액 기준 중위소득 60% 이하 (재산 1억 2,200만원 이하)",
            "원가구 기준 중위소득 100% 이하 (재산 4억 7,000만원 이하, 만 30세 이상 등 예외)"
        ],
        "application_steps": [
            "1단계: 복지로(bokjiro.go.kr) 접속 후 복지서비스 모의계산 자격 자가진단",
            "2단계: 청년월세 한시 특별지원 신청서 및 증빙자료 파일 첨부",
            "3단계: 관할 지자체 서류 심사 및 소득·재산 조사 (약 30~45일)",
            "4단계: 선정 결과 통보 후 매월 25일 청년 본인 계좌로 지원금 입금"
        ],
        "required_documents": [
            "임대차계약서 사본 (확정일자 필수)",
            "최근 3개월간 월세 이체 내역서(통장 거래내역)",
            "가족관계증명서 (청년 본인 및 부모 기준 각 1부)",
            "통장 사본"
        ],
        "caution_notes": [
            "주택 소유자, 공공임대주택 거주자, 지자체 자체 월세 지원 수혜자는 중복 지원 불가합니다.",
            "부모와 함께 주민등록상 동거 중인 청년은 지원 대상에서 제외됩니다."
        ],
        "score": 93.0
    },
    {
        "service_id": "WELFARE-EARNED-INCOME-04",
        "service_name": "근로장려금 및 자녀장려금",
        "category": "소득지원·세제혜택",
        "target_summary": "일하는 저소득 근로자, 사업자 가구 중 소득 및 가구원 재산 합계 2.4억원 미만 가구",
        "benefit_summary": "단독가구 최대 165만원, 홑벌이가구 최대 285만원, 맞벌이가구 최대 330만원 현금 환급 지급 (자녀장려금 자녀 1인당 최대 100만원 추가)",
        "benefit_highlight": "맞벌이 가구 최대 330만원 + 자녀 1인당 최대 100만원 현금 환급",
        "application_period": "정기신청: 매년 5월 1일 ~ 5월 31일 / 반기신청: 상반기 9월, 하반기 3월",
        "apply_url": "https://www.hometax.go.kr",
        "inquiry_contact": "국세청 장려금 상담센터 (1566-3636)",
        "competent_agency": "국세청",
        "eligibility_checklist": [
            "단독가구: 총소득 2,200만원 미만",
            "홑벌이가구: 총소득 3,200만원 미만",
            "맞벌이가구: 총소득 3,800만원(2024 귀속 4,400만원 상향안 적용) 미만",
            "가구원 전원의 전년도 6월 1일 기준 재산 합계액 2억 4천만원 미만 (부채 차감 안 됨)"
        ],
        "application_steps": [
            "1단계: 국세청 홈택스(손택스 앱) 로그인",
            "2단계: [신청/제출] -> [근로·자녀장려금] 정기 또는 반기 신청 메뉴 접속",
            "3단계: 소득 및 가구원 정보 자동 확인 후 수령 계좌번호 등록",
            "4단계: 국세청 심사 후 8월 말(정기) 또는 6월 말(반기) 계좌 즉시 입금"
        ],
        "required_documents": [
            "신청안내문 수신자는 개별인증번호로 무서류 간편 신청 가능",
            "미수신자는 급여통장 사본, 소득 증빙서류 및 임대차계약서(전세금 확인용) 첨부"
        ],
        "caution_notes": [
            "가구원 재산 합계가 1억 7천만원 이상 2억 4천만원 미만인 경우 산정 장려금의 50%만 감액 지급됩니다.",
            "기한 후 신청(6월~11월) 시 장려금의 10%가 감액되므로 5월 정기 기간 내 신청이 필수입니다."
        ],
        "score": 96.0
    },
    {
        "service_id": "WELFARE-PARENTAL-PAY-05",
        "service_name": "부모급여 및 아동수당",
        "category": "출산·보육지원",
        "target_summary": "만 0~1세 영아(0~23개월)를 양육하는 대한민국 모든 부모 (소득·재산 기준 없음)",
        "benefit_summary": "만 0세(0~11개월): 매월 100만원 현금 지급 / 만 1세(12~23개월): 매월 50만원 현금 지급 (만 8세 미만 아동수당 월 10만원 중복 지급)",
        "benefit_highlight": "만 0세 월 100만원, 만 1세 월 50만원 100% 현금 지급 (소득무관)",
        "application_period": "출생일 포함 60일 이내 신청 시 출생월부터 소급 지급",
        "apply_url": "https://www.bokjiro.go.kr",
        "inquiry_contact": "보건복지상담센터 (129)",
        "competent_agency": "보건복지부",
        "eligibility_checklist": [
            "출생 후 만 0세(0~11개월) 및 만 1세(12~23개월) 아동의 부모",
            "부모의 소득 및 재산 수준과 무관하게 100% 전액 지원",
            "어린이집 이용 시 보육료 바우처 차액만큼 부모 계좌로 현금 입금"
        ],
        "application_steps": [
            "1단계: 출생신고 시 '행복출산 원스톱 서비스'로 주민센터 또는 정부24에서 일괄 신청",
            "2단계: 복지로(bokjiro.go.kr) 웹사이트 또는 모바일 앱 접속",
            "3단계: [복지서비스 신청] -> [영유아] -> [부모급여] 선택 후 부모 명의 계좌 입력",
            "4단계: 매월 25일 지정 계좌로 현금 입금"
        ],
        "required_documents": [
            "출생증명서 (출생신고와 동시 신청 시 자동 갈음)",
            "부모 신분증 및 입금 통장 사본"
        ],
        "caution_notes": [
            "출생일로부터 60일이 지난 후 신청하면 신청 월부터 지급되므로 60일 이내 신청이 중요합니다.",
            "아동수당(월 10만원)과 첫만남이용권(첫째 200만/둘째 300만원)은 부모급여와 전액 중복 수령 가능합니다."
        ],
        "score": 97.0
    },
    {
        "service_id": "WELFARE-KPASS-TRANSIT-06",
        "service_name": "K-패스 (대중교통비 환급 지원)",
        "category": "교통·생활복지",
        "target_summary": "전국 만 19세 이상 대중교통(지하철, 버스, 신분당선, 광역버스, GTX) 이용 국민",
        "benefit_summary": "월 15회 이상 대중교통 이용 시 지출금액의 20%~53% 다음 달 사후 현금 환급 (일반 20%, 청년 만19~34세 30%, 저소득층 53% 환급)",
        "benefit_highlight": "대중교통비 최대 53% 현금 환급 (일반 20%, 청년 30%, 저소득 53%)",
        "application_period": "K-패스 전용 카드 발급 후 앱 등록 시 즉시 적용",
        "apply_url": "https://korea-pass.kr",
        "inquiry_contact": "한국교통안전공단 (054-459-7114)",
        "competent_agency": "국토교통부 대도시권광역교통위원회",
        "eligibility_checklist": [
            "만 19세 이상 대한민국 거주 국민",
            "월 15회 이상 대중교통(시내버스, 마을버스, 지하철, 광역버스, GTX 등) 이용자 (월 최대 60회 인정)",
            "청년층(만 19~34세)은 연령 인증 시 30% 환급율 자동 적용",
            "기초생활수급자 및 차상위계층은 증빙 시 53% 최대 환급율 적용"
        ],
        "application_steps": [
            "1단계: 취급 10개 카드사(신한, 국민, 우리, 하나, 삼성, 현대, 농협 등)에서 K-패스 전용 카드 발급",
            "2단계: K-패스 공식 앱 또는 웹사이트(korea-pass.kr) 회원가입",
            "3단계: 발급받은 카드번호 16자리 등록 완료",
            "4단계: 평소처럼 카드로 대중교통 탑승 (다음 달 결제계좌로 환급금 자동 입금 또는 청구할인)"
        ],
        "required_documents": [
            "본인 명의 K-패스 카드",
            "저소득층의 경우 국민기초생활수급자 증명서 (정부24 연계 자동 확인)"
        ],
        "caution_notes": [
            "월 이용 횟수가 15회 미만인 달에는 환급 혜택이 이월되지 않고 소멸됩니다.",
            "고속버스, KTX, SRT 등 별도 승차권 발권 교통수단은 환급 대상에서 제외됩니다."
        ],
        "score": 92.0
    },
    {
        "service_id": "WELFARE-BASIC-PENSION-07",
        "service_name": "기초연금",
        "category": "시니어·노후소득보장",
        "target_summary": "만 65세 이상 어르신 중 가구 소득인정액이 선정기준액(단독가구 213만원, 부부가구 340.8만원) 이하인 가구",
        "benefit_summary": "단독가구 매월 최대 334,810원, 부부가구 매월 최대 535,680원 평생 현금 입금 지급 (매월 25일 지급)",
        "benefit_highlight": "만 65세 이상 어르신 단독 최대 33.4만원, 부부 최대 53.5만원 평생 매월 지급",
        "application_period": "만 65세 생일이 속한 달의 1개월 전부터 상시 신청 가능",
        "apply_url": "https://www.bokjiro.go.kr",
        "inquiry_contact": "국민연금공단 콜센터 (1355) 또는 보건복지상담센터 (129)",
        "competent_agency": "보건복지부 / 국민연금공단",
        "eligibility_checklist": [
            "대한민국 국적 만 65세 이상 어르신",
            "가구의 소득평가액과 재산의 월 소득환산액 합계가 선정기준액 이하",
            "공무원연금, 군인연금, 사학연금 등 직역연금 수급권자 및 배우자는 원칙적 제외"
        ],
        "application_steps": [
            "1단계: 주소지 관할 읍·면·동 행정복지센터 또는 국민연금공단 지사 방문 (복지로 온라인 신청 가능)",
            "2단계: 사회보장급여 신청서 및 소득·재산 신고서, 금융정보 제공 동의서 작성",
            "3단계: 지자체 소득·재산 조사 (약 30일 소요)",
            "4단계: 수급 결정 통지 후 매월 25일 어르신 본인 명의 계좌로 입금"
        ],
        "required_documents": [
            "신분증 (주민등록증 또는 운전면허증)",
            "기초연금 수령 희망 통장 사본",
            "배우자의 금융정보 제공 동의서 (배우자 유무 시 필수)",
            "전월세 임대차계약서 (해당자)"
        ],
        "caution_notes": [
            "만 65세가 되기 1달 전부터 신청 가능하며 신청 월부터 지급되므로 미리 신청하는 것이 유리합니다."
        ],
        "score": 98.0
    },
    {
        "service_id": "WELFARE-SMALL-BIZ-08",
        "service_name": "소상공인 정책자금 저금리 대환대출",
        "category": "소상공인·경영안정",
        "target_summary": "중소벤처기업부 소상공인 기준을 충족하며 7% 이상 고금리 대출을 성실 상환 중인 영세 자영업자",
        "benefit_summary": "연 4.5% 고정금리로 10년 분할상환(거치기간 최대 5년) 전환 지원, 1인당 최대 5,000만원 한도 대환",
        "benefit_highlight": "7% 이상 고금리 대출을 4.5% 저금리 장기분할상환으로 대환 (최대 5,000만원)",
        "application_period": "소상공인정책자금 누리집 분기별 한도 소진 시까지",
        "apply_url": "https://ols.semas.or.kr",
        "inquiry_contact": "소상공인시장진흥공단 (1357)",
        "competent_agency": "중소벤처기업부 / 소상공인시장진흥공단",
        "eligibility_checklist": [
            "사업자등록증 보유 정상 영업 중인 소상공인",
            "신용보증재단 또는 2금융권 7% 이상 대출 성실 상환 중인 자",
            "국세 및 지방세 체납 사실이 없는 자"
        ],
        "application_steps": [
            "1단계: 소상공인정책자금 사이트 회원가입 및 정책자금 지원대상 확인서 발급",
            "2단계: 취급 시중은행(국민, 신한, 우리, 하나 등) 앱에서 대환대출 심사 접수",
            "3단계: 대출 승인 시 기존 고금리 채무 즉시 전액 상환 대환"
        ],
        "required_documents": [
            "사업자등록증명원",
            "부가가치세과세표준증명원",
            "기존 고금리 금융거래확인서"
        ],
        "caution_notes": [
            "연체 이력이나 신용점수 하위 구간에 따라 대출 한도가 축소될 수 있습니다."
        ],
        "score": 95.0
    },
    {
        "service_id": "WELFARE-ELEC-SUPPORT-09",
        "service_name": "소상공인 전기요금 특별지원",
        "category": "소상공인·공과금지원",
        "target_summary": "연 매출 6,000만원 이하 소상공인 중 사업장 전기요금 계약자 (일반용, 산업용, 농사용)",
        "benefit_summary": "사업장 당 최대 20만원 전기요금 고지서 차감 또는 계좌 직접 환급 지원",
        "benefit_highlight": "영세 소상공인 사업장 전기요금 최대 20만원 한시 전액 차감",
        "application_period": "소상공인전기요금특별지원.kr 온라인 상시 접수",
        "apply_url": "https://소상공인전기요금특별지원.kr",
        "inquiry_contact": "전기요금 특별지원 콜센터 (1533-0200)",
        "competent_agency": "중소벤처기업부",
        "eligibility_checklist": [
            "개업일이 2023년 12월 31일 이전인 정상 영업 소상공인",
            "2022년 또는 2023년 연 매출액 6,000만원 이하",
            "사업장 명의 한전 계약자 또는 관리비 합산 납부자"
        ],
        "application_steps": [
            "1단계: 전용 웹사이트(소상공인전기요금특별지원.kr) 접속",
            "2단계: 사업자등록번호 및 한전 고객번호 입력",
            "3단계: 대상자 검증 완료 후 다음 달 고지서부터 최대 20만원 자동 차감"
        ],
        "required_documents": [
            "사업자등록증 사본",
            "전기요금 납부영수증 (관리비 합산 납부자의 경우 관리비 고지서)"
        ],
        "caution_notes": [
            "1인이 다수 사업장을 운영하는 경우 1개 사업장에 한하여 지원됩니다."
        ],
        "score": 94.0
    },
    {
        "service_id": "WELFARE-ELDERLY-CARE-10",
        "service_name": "노인장기요양보험 혜택 및 간병비 지원",
        "category": "시니어·돌봄복지",
        "target_summary": "만 65세 이상 노인 또는 만 65세 미만 노인성 질병(치매, 뇌혈관질환, 파킨슨 등)으로 일상생활이 어려운 어르신",
        "benefit_summary": "장기요양 1~5등급 판정 시 방문요양(요양보호사 가정 방문), 주야간보호센터, 복지용구 구매 비용의 85~100% 국비 지원",
        "benefit_highlight": "요양보호사 방문 및 간병비용 최대 85~100% 국비 바우처 지원",
        "application_period": "국민건강보험공단 지사 전국 상시 접수",
        "apply_url": "https://www.longtermcare.or.kr",
        "inquiry_contact": "국민건강보험공단 (1577-1000)",
        "competent_agency": "보건복지부 / 국민건강보험공단",
        "eligibility_checklist": [
            "만 65세 이상 어르신 또는 노인성 질환 보유 65세 미만 국민",
            "거동이 현저히 불편하여 6개월 이상 스스로 일상생활 수행이 곤란한 상태",
            "공단 직원의 방문 조사 및 등급판정위원회 심의를 거쳐 1~5등급 인정"
        ],
        "application_steps": [
            "1단계: 국민건강보험공단 장기요양보험 운영센터 방문 또는 온라인/팩스 신청",
            "2단계: 공단 간호사/사회복지사가 어르신 거주지 직접 방문하여 일상수행평가 조사",
            "3단계: 의사소견서 제출 및 등급판정위원회 심의 (신청 후 30일 이내 등급 통보)",
            "4단계: 장기요양인정서 수령 후 관할 재가요양기관 계약 및 요양보호사 파견 서비스 개시"
        ],
        "required_documents": [
            "장기요양인정신청서",
            "의사소견서 (공단 안내 후 지정 기한 내 제출)"
        ],
        "caution_notes": [
            "일반 수급자는 비용의 15%만 본인 부담하며, 기초생활수급자는 본인 부담금이 전액 면제됩니다."
        ],
        "score": 97.0
    },
    {
        "service_id": "WELFARE-SENIOR-JOB-11",
        "service_name": "시니어 공공일자리 및 어르신 사회활동 지원",
        "category": "시니어·일자리",
        "target_summary": "만 65세 이상(일부 만 60세 이상) 기초연금 수급 어르신 중 건강하게 사회활동 참여를 희망하는 분",
        "benefit_summary": "공익활동형 월 30시간 참여 시 월 29만원 지급 / 사회서비스형 월 60시간 참여 시 주휴수당 포함 월 최대 76만원 급여 지급",
        "benefit_highlight": "어르신 맞춤형 공공일자리 참여 시 매월 29만~76만원 활동비 지급",
        "application_period": "매년 12월 정기모집 및 연중 결원 발생 시 수시 추가 모집",
        "apply_url": "https://www.seniorro.or.kr",
        "inquiry_contact": "한국노인인력개발원 (1544-3388)",
        "competent_agency": "보건복지부 / 한국노인인력개발원",
        "eligibility_checklist": [
            "공익활동: 만 65세 이상 기초연금 수급자",
            "사회서비스형: 만 65세 이상 (일부 사업 60세 이상)",
            "생계급여 수급자 및 직장건강보험 가입자는 일부 사업 참여 제한"
        ],
        "application_steps": [
            "1단계: 시니어클럽, 노인복지관, 대한노인회 등 거주지 인근 수행기관 방문 접수",
            "2단계: 노인일자리여기(seniorro.or.kr) 온라인 통합 검색 및 신청",
            "3단계: 소득, 건강 상태, 세대 구성원 심사 후 고득점자 우선 선발",
            "4단계: 직무 교육 수료 후 사업장 배치 및 매월 급여 통장 입금"
        ],
        "required_documents": [
            "참여신청서 (수행기관 비치)",
            "주민등록등본 1부",
            "기초연금 수급확인서"
        ],
        "caution_notes": [
            "동일인이 타 정부 재정지원 일자리 사업과 중복 참여하는 것은 엄격히 금지됩니다."
        ],
        "score": 93.0
    },
    {
        "service_id": "WELFARE-YELLOW-UMBRELLA-12",
        "service_name": "소상공인 노란우산공제 및 희망장려금",
        "category": "소상공인·퇴직금공제",
        "target_summary": "소기업·소상공인 사업체 대표자 (자영업자, 소상공인, 프리랜서, 간이과세자 모두 가능)",
        "benefit_summary": "연간 최대 500만원 소득공제로 100만원 이상 절세 효과 + 폐업 시 복리 이자 퇴직금 수령 + 지자체 희망장려금 매월 1~2만원 추가 적립",
        "benefit_highlight": "최대 500만원 소득공제 절세 혜택과 폐업 시 복리이자 목돈 보호",
        "application_period": "연중 상시 가입 가능",
        "apply_url": "https://www.8899.or.kr",
        "inquiry_contact": "중소기업중앙회 노란우산 콜센터 (1666-9988)",
        "competent_agency": "중소벤처기업부 / 중소기업중앙회",
        "eligibility_checklist": [
            "소기업·소상공인 기준에 해당하는 개인사업자 및 법인 대표",
            "유흥주점업, 도박장업 등 일부 사행성 업종 제외 전 업종 가입 가능",
            "부금 월 5만원 ~ 100만원 (1만원 단위 선택 가능)"
        ],
        "application_steps": [
            "1단계: 노란우산 공식 홈페이지(8899.or.kr) 또는 시중은행 창구 가입",
            "2단계: 자동이체 부금 납입액 설정",
            "3단계: 가입 승인 시 소속 지자체 희망장려금 자동 신청 연계",
            "4단계: 연말정산 및 5월 종합소득세 신고 시 소득공제 자동 반영"
        ],
        "required_documents": [
            "사업자등록증 사본",
            "원천징수이행상황신고서 또는 부가가치세과세표준증명"
        ],
        "caution_notes": [
            "공제금은 법률에 의해 압류, 양도, 담보 제공이 전면 금지되어 폐업 시에도 안전하게 지켜집니다."
        ],
        "score": 96.0
    },
    {
        "service_id": "WELFARE-PENSION-REFORM-13",
        "service_name": "국민연금 모수개혁 로드맵 및 세대별 보험료율·소득대체율 개편안",
        "category": "연금·노후보장",
        "target_summary": "대한민국 국민연금 전체 가입자 (직장가입자, 지역가입자, 임의가입자)",
        "benefit_summary": "보험료율 9%에서 13% 단계적 현실화 로드맵 및 소득대체율 42% 수준 유지, 국가 지급보장 명문화 추진",
        "benefit_highlight": "국가 지급보장 법제화 및 세대별 차등 인상률 적용으로 지속가능한 노후소득 보장",
        "application_period": "개혁 법안 시행 로드맵에 따른 단계별 적용",
        "apply_url": "https://www.nps.or.kr",
        "inquiry_contact": "국민연금공단 (1355)",
        "competent_agency": "보건복지부 / 국민연금공단",
        "eligibility_checklist": [
            "만 18세 이상 60세 미만 대한민국 거주 국민",
            "청년층, 중장년층 연령대별 보험료율 인상 속도 차등 적용 방안 확인",
            "출산크레딧(첫째 아이부터 인정) 및 군복무크레딧 확대 혜택"
        ],
        "application_steps": [
            "1단계: 국민연금공단 '내 곁에 국민연금' 앱 접속",
            "2단계: 본인 예상 연금 수령액 및 가입 기간 조회",
            "3단계: 추후납부(추납) 및 반환일시금 반납을 통한 가입 기간 연장 전략 수립"
        ],
        "required_documents": [
            "신분증",
            "추납 또는 임의가입 신청서 (해당자)"
        ],
        "caution_notes": [
            "가입 기간이 10년(120개월) 미만이면 만 65세 도달 시 연금이 아닌 일시금으로만 수령되므로 10년 채우기가 필수입니다."
        ],
        "score": 98.0
    },
    {
        "service_id": "WELFARE-HOUSING-NEWHOME-14",
        "service_name": "청년·신혼부부 공공분양 뉴:홈 공급 로드맵 및 특별공급 청약 가이드",
        "category": "주거복지·청약",
        "target_summary": "만 19~39세 무주택 청년, 혼인 7년 이내 신혼부부, 예비신혼부부",
        "benefit_summary": "시세의 70~80% 분양가 공급, 연 1.9~3.0% 초저리 장기 모기지(최대 5억원, 40년 만기) 지원 (나눔형, 선택형, 일반형)",
        "benefit_highlight": "시세 대비 70% 저렴한 분양가와 1%대 초저리 모기지로 내 집 마련",
        "application_period": "LH청약플러스 및 SH서울주택도시공사 분기별 사전청약 공고",
        "apply_url": "https://apply.lh.or.kr",
        "inquiry_contact": "LH 콜센터 (1600-1004) / 마이홈 (1600-1004)",
        "competent_agency": "국토교통부 / 한국토지주택공사(LH)",
        "eligibility_checklist": [
            "입주자모집공고일 현재 무주택 세대구성원",
            "청년 특별공급: 과거 주택 소유 이력이 없는 자 (소득 140% 이하, 순자산 2억 8,900만원 이하)",
            "신혼부부 특별공급: 혼인 기간 7년 이내 또는 6세 이하 자녀 보유"
        ],
        "application_steps": [
            "1단계: LH청약플러스(apply.lh.or.kr) 회원가입 및 공동인증서 로그인",
            "2단계: 공급 유형(나눔형, 선택형, 일반형)별 청약 자격 진단",
            "3단계: 인터넷 청약 신청 및 당첨자 발표 확인"
        ],
        "required_documents": [
            "주민등록표등본 및 초본",
            "가족관계증명서(상세)",
            "소득금액증명원 및 건강보험자격득실확인서"
        ],
        "caution_notes": [
            "나눔형의 경우 의무거주기간 5년 이후 환매 시 처분손익의 70%가 수분양자에게 귀속됩니다."
        ],
        "score": 96.5
    },
    {
        "service_id": "WELFARE-CARE-CHILD-15",
        "service_name": "초등 늘봄학교 전국 전면 확대 및 영유아 유보통합 돌봄 지원 가이드",
        "category": "보육·교육복지",
        "target_summary": "초등학교 재학 아동(초등 1~2학년 우선 지원) 및 만 0~5세 영유아 가구",
        "benefit_summary": "정규 수업 전후 아침·저녁 최장 오후 8시까지 맞춤형 돌봄 및 교육 프로그램 100% 무상 지원 (매일 2시간 무료)",
        "benefit_highlight": "희망하는 모든 초등학생 최장 오후 8시까지 학교 안심 돌봄 및 맞춤 교육 무료 제공",
        "application_period": "매 학기 초 학교 알리미 및 교육지원청 접수",
        "apply_url": "https://www.moe.go.kr",
        "inquiry_contact": "교육부 늘봄학교 콜센터 (02-6222-6060)",
        "competent_agency": "교육부 / 시도교육청",
        "eligibility_checklist": [
            "해당 초등학교 재학 1~2학년 전체 희망 학생 (단계적 전 학년 확대)",
            "맞벌이, 저소득 가구 등 우선 지원 요건 증빙 불필요 (누구나 신청 가능)"
        ],
        "application_steps": [
            "1단계: 소속 학교 안내 가정통신문 및 늘봄학교 신청 링크 접속",
            "2단계: 희망 시간대(아침 돌봄, 방과후 돌봄, 저녁 돌봄) 및 맞춤형 강좌 선택",
            "3단계: 프로그램 배정 확정 후 학교 내 전용 교실에서 수업 참여"
        ],
        "required_documents": [
            "늘봄학교 참여 신청서 (온라인 제출)"
        ],
        "caution_notes": [
            "석식 지원 및 저녁 돌봄 귀가 시 보호자 동행 수칙을 준수해야 합니다."
        ],
        "score": 95.0
    }
]


class WelfareCollector:
    """Discovers, normalizes, and curates Korean government welfare policies (data.go.kr & gov24)."""

    def __init__(self, use_remote_feed: bool = True, gov24_client: Optional[Gov24WelfareClient] = None):
        self.use_remote_feed = use_remote_feed
        self.gov24_client = gov24_client or gov24_welfare_client

    async def health_check(self) -> Dict[str, Any]:
        """Verify welfare data availability, Gov24 OpenAPI, and upstream public feed connectivity."""
        is_gov24_ok = False
        try:
            sample = await self.gov24_client.search_services("청년", page=1, per_page=1)
            is_gov24_ok = len(sample) > 0
        except Exception:
            is_gov24_ok = False

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get("https://www.korea.kr/rss/policy.xml")
                is_feed_ok = res.status_code == 200
        except Exception:
            is_feed_ok = False

        return {
            "success": True,
            "gov24_api_available": is_gov24_ok,
            "catalog_count": len(CORE_WELFARE_CATALOG),
            "remote_feed_available": is_feed_ok,
            "message": f"복지 수집기 정상 작동 중 (정부24 OpenAPI: {'정상 연동' if is_gov24_ok else '오프라인'}, 카탈로그 {len(CORE_WELFARE_CATALOG)}건 보유)"
        }

    async def get_popular_programs(self, limit: int = 10) -> List[WelfareCandidateItem]:
        """Fetch high-priority popular welfare and benefit policies."""
        items: List[WelfareCandidateItem] = []
        for raw in CORE_WELFARE_CATALOG[:limit]:
            items.append(WelfareCandidateItem.model_validate(raw))
        return items

    async def get_program_by_id(self, service_id: str) -> Optional[WelfareCandidateItem]:
        """Lookup specific welfare program by its service ID (supporting Gov24 and Catalog)."""
        # 1. First check curated catalog
        for raw in CORE_WELFARE_CATALOG:
            if raw["service_id"] == service_id:
                return WelfareCandidateItem.model_validate(raw)

        # 2. Second, try Gov24 detail if ID looks like a Gov24 service ID (numeric or >= 8 chars)
        if self.gov24_client and (service_id.isdigit() or len(service_id) >= 8):
            try:
                detail = await self.gov24_client.get_service_detail(service_id)
                if detail:
                    s_name = detail.get("서비스명", "")
                    ministry = detail.get("소관기관명", "대한민국 정부")
                    target = detail.get("지원대상") or "관련 요건 충족 국민"
                    benefit = detail.get("지원내용") or detail.get("서비스목적") or "정부 공식 지원금 및 바우처"
                    checklist = self.gov24_client.extract_checklist(detail.get("선정기준"), target)
                    steps = self.gov24_client.extract_steps(detail.get("신청방법"))
                    docs = self.gov24_client.extract_documents(detail.get("구비서류"))
                    phone = self.gov24_client.extract_phone(detail.get("문의처"))
                    apply_url = detail.get("온라인신청사이트URL") or "https://www.bokjiro.go.kr"
                    stats_box = self.gov24_client.get_grounding_stats_box(s_name, ministry)

                    return WelfareCandidateItem(
                        service_id=service_id,
                        service_name=s_name,
                        category=detail.get("서비스분야", "정부지원"),
                        target_summary=self.gov24_client.clean_text(target)[:160],
                        benefit_summary=self.gov24_client.clean_text(benefit)[:200],
                        benefit_highlight=self.gov24_client.clean_text(s_name),
                        application_period=detail.get("신청기한", "상시신청"),
                        apply_url=apply_url,
                        inquiry_contact=phone,
                        competent_agency=ministry,
                        eligibility_checklist=checklist,
                        application_steps=steps,
                        required_documents=docs,
                        caution_notes=[
                            f"본 정책은 {ministry} 소관으로 변경사항 발생 시 복지로에서 최신 공고를 확인하세요.",
                            f"문의: {phone}"
                        ],
                        stats_fact_box=stats_box,
                        legal_basis=detail.get("법령"),
                        score=95.0,
                        source_attribution=f"대한민국 공공데이터포털(data.go.kr) & {ministry}"
                    )
            except Exception as e:
                logger.warning("Error fetching Gov24 program by id %s: %s", service_id, str(e))
        return None

    async def discover_policies_from_gov24(self, queries: List[str], limit: int = 15) -> List[WelfareCandidateItem]:
        """Fetch live official welfare programs from Gov24 / data.go.kr OpenAPI."""
        results: List[WelfareCandidateItem] = []
        seen_ids = set()

        for q in queries:
            try:
                raw_list = await self.gov24_client.search_services(query=q, per_page=4, central_only=True)
                for item in raw_list:
                    s_id = str(item.get("서비스ID", "")).strip()
                    s_name = str(item.get("서비스명", "")).strip()
                    if not s_id or s_id in seen_ids:
                        continue
                    seen_ids.add(s_id)

                    # Fetch detail for rich checklist and documents
                    detail = await self.gov24_client.get_service_detail(s_id) or {}
                    ministry = item.get("소관기관명") or "대한민국 정부"
                    category = item.get("서비스분야") or "정부지원"
                    target = detail.get("지원대상") or item.get("지원대상") or "해당 요건을 충족하는 대한민국 국민"
                    benefit = detail.get("지원내용") or item.get("지원내용") or item.get("서비스목적요약") or "정부 공식 지원 혜택"
                    summary = item.get("서비스목적요약") or benefit[:150]
                    period = detail.get("신청기한") or item.get("신청기한") or "상시 접수"
                    apply_url = detail.get("온라인신청사이트URL") or item.get("상세조회URL") or "https://www.bokjiro.go.kr"
                    if not apply_url.startswith("http"):
                        apply_url = "https://www.bokjiro.go.kr"

                    phone = self.gov24_client.extract_phone(detail.get("문의처") or item.get("전화문의"))
                    checklist = self.gov24_client.extract_checklist(detail.get("선정기준") or item.get("선정기준"), target)
                    steps = self.gov24_client.extract_steps(detail.get("신청방법") or item.get("신청방법"))
                    docs = self.gov24_client.extract_documents(detail.get("구비서류"))
                    stats_box = self.gov24_client.get_grounding_stats_box(s_name, ministry)
                    legal = detail.get("법령")

                    c_notes = [
                        f"본 정책은 {ministry} 소관으로 예산 소진 상황에 따라 신청 접수가 조기 마감될 수 있습니다.",
                        "유사 정부지원금 및 지자체 바우처와 중복 수혜 가능 여부를 사전 확인하시기 바랍니다.",
                        f"세부 문의사항은 관할 주민센터 또는 {phone}에서 공식 상담 가능합니다."
                    ]

                    results.append(
                        WelfareCandidateItem(
                            service_id=s_id,
                            service_name=s_name,
                            category=category,
                            target_summary=self.gov24_client.clean_text(target)[:160],
                            benefit_summary=self.gov24_client.clean_text(benefit)[:200],
                            benefit_highlight=self.gov24_client.clean_text(summary)[:120],
                            application_period=period,
                            apply_url=apply_url,
                            inquiry_contact=phone,
                            competent_agency=ministry,
                            eligibility_checklist=checklist,
                            application_steps=steps,
                            required_documents=docs,
                            caution_notes=c_notes,
                            stats_fact_box=stats_box,
                            legal_basis=legal,
                            score=92.0 + min(len(checklist) * 2, 6),
                            source_attribution=f"대한민국 공공데이터포털(data.go.kr) & {ministry}"
                        )
                    )
                    if len(results) >= limit:
                        break
            except Exception as e:
                logger.warning("Error discovering Gov24 policies for query '%s': %s", q, str(e))
            if len(results) >= limit:
                break

        return results

    async def discover_policies_for_site(self, site_id: int, limit: int = 20) -> List[WelfareCandidateItem]:
        """Discover site-specialized welfare programs for Welfare23, Welfare24, Welfare25."""
        if site_id == 5:  # Welfare23 (청년/주거/취업/학자금)
            queries = ["청년", "취업", "주거", "일자리", "자산형성", "학자금"]
        elif site_id == 6:  # Welfare24 (시니어/소상공인/연금/노후)
            queries = ["기초연금", "소상공인", "어르신", "노후", "재기", "연금"]
        elif site_id == 7:  # Welfare25 (보육/아동/바우처/의료/건강보험)
            queries = ["보육", "아동", "영유아", "바우처", "의료", "건강", "부모급여"]
        else:
            queries = ["지원", "복지", "바우처"]

        try:
            gov_candidates = await self.discover_policies_from_gov24(queries, limit=limit)
            if gov_candidates:
                return gov_candidates
        except Exception as e:
            logger.warning("Gov24 site discovery error for site %d: %s (falling back)", site_id, str(e))

        # Fallback to curated catalog
        all_curated = await self.get_popular_programs(limit=30)
        filtered = []
        for c in all_curated:
            if site_id == 5 and any(k in c.service_name for k in ["청년", "주거", "취업", "도약", "학자금"]):
                filtered.append(c)
            elif site_id == 6 and any(k in c.service_name for k in ["시니어", "연금", "소상공인", "장려금", "노후", "어르신"]):
                filtered.append(c)
            elif site_id == 7 and any(k in c.service_name for k in ["바우처", "K-패스", "부모급여", "생활", "긴급", "문화누리", "늘봄"]):
                filtered.append(c)
        return filtered or all_curated[:limit]

    async def discover_latest_policies(self, limit: int = 20) -> List[WelfareCandidateItem]:
        """Discover latest live policies from Gov24 OpenAPI, government RSS, or verified catalog."""
        try:
            gov_candidates = await self.discover_policies_from_gov24(
                ["청년", "연금", "보육", "소상공인", "바우처", "의료"],
                limit=limit
            )
            if len(gov_candidates) >= 5:
                return gov_candidates
        except Exception as e:
            logger.warning("Gov24 general discovery failed: %s (falling back to RSS/catalog)", str(e))

        candidates = await self.get_popular_programs(limit=limit)
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:limit]
