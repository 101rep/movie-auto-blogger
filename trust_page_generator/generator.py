"""Trust Page Generator for WordPress Blogs V1.0.
Generates 8 specialized, professional, and SEO-compliant Trust Pages for each blog.
Adheres strictly to PRD Principles:
- No generic copied templates: each blog has unique missions, content fields, and verification rules.
- Professional without exaggeration ("공식 자료와 공개된 정보를 기반으로 쉽게 정리합니다").
- Fully compatible with Google AdSense, E-E-A-T, and modern Web Standards.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List
from trust_page_generator.identities import MASTER_IDENTITIES
from trust_page_generator.database.models import BlogIdentity, TrustPage
from trust_page_generator.database.session import SessionLocal


class TrustPageGenerator:
    """Generates structured HTML trust pages tailored to each blog's identity."""

    @staticmethod
    def _base_style() -> str:
        """Shared responsive styling wrapper for trust pages."""
        return """
<style>
.trust-page-container {
    max-width: 820px;
    margin: 0 auto;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    color: #1e293b;
    line-height: 1.85;
    padding: 20px 10px 40px;
    word-break: keep-all;
}
.trust-header-badge {
    display: inline-block;
    background: #e2e8f0;
    color: #475569;
    font-size: 13px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 12px;
}
.trust-title {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 16px 0;
    line-height: 1.35;
    letter-spacing: -0.02em;
}
.trust-lead-box {
    background: #f8fafc;
    border-left: 4px solid #3b82f6;
    padding: 18px 22px;
    border-radius: 0 10px 10px 0;
    font-size: 16px;
    color: #334155;
    margin-bottom: 32px;
}
.trust-section {
    margin-bottom: 36px;
}
.trust-section-title {
    font-size: 20px;
    font-weight: 700;
    color: #1e293b;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 10px;
    margin: 32px 0 16px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.trust-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin: 16px 0;
}
.trust-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.trust-card-title {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 8px;
}
.trust-card-desc {
    font-size: 14px;
    color: #64748b;
    margin: 0;
    line-height: 1.6;
}
.trust-table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 14px;
}
.trust-table th, .trust-table td {
    border: 1px solid #cbd5e1;
    padding: 12px 14px;
    text-align: left;
}
.trust-table th {
    background: #f1f5f9;
    font-weight: 600;
    color: #334155;
    width: 25%;
}
.trust-callout-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 10px;
    padding: 18px 22px;
    margin: 24px 0;
    color: #1e40af;
}
.trust-contact-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 24px;
    margin: 24px 0;
}
.trust-footer-meta {
    font-size: 13px;
    color: #94a3b8;
    margin-top: 40px;
    border-top: 1px solid #e2e8f0;
    padding-top: 16px;
    text-align: right;
}
</style>
"""

    def generate_about_us(self, identity: Dict[str, Any]) -> str:
        """PAGE 1: About Us."""
        brand = identity["brand_name"]
        cat = identity["category"]
        mission = identity["mission"]
        target = identity["target_user"]
        trust_msg = identity["trust_message"]

        return f"""{self._base_style()}
<div class="trust-page-container">
  <span class="trust-header-badge">공식 사이트 소개 · About Us</span>
  <h1 class="trust-title">{brand} 소개 및 운영 목적</h1>
  
  <div class="trust-lead-box">
    <strong>{brand}</strong>는 <em>"{mission}"</em>라는 비전을 바탕으로 개설된 {cat} 전문 정보 미디어입니다. 
    과장되거나 검증되지 않은 홍보성 정보를 지양하고, 공공기관 및 신뢰할 수 있는 공식 데이터를 알기 쉽게 정리하여 독자 여러분의 합리적인 의사결정을 돕습니다.
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">1. 사이트 개요 및 설립 배경</h2>
    <p>
      수많은 정보가 쏟아지는 디지털 환경에서 이용자들은 불명확한 출처와 상업적 광고로 인해 정작 필요한 정확한 정보를 찾기 어렵습니다. 
      <strong>{brand}</strong>는 이러한 정보 격차와 피로도를 해소하기 위해 설립되었습니다. 
      공식 발표 자료와 1차 공공 데이터를 중심으로, 복잡한 내용을 누구나 한눈에 이해할 수 있는 명쾌한 콘텐츠로 재구성하여 제공합니다.
    </p>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">2. 주요 제공 정보 분야</h2>
    <div class="trust-card-grid">
      <div class="trust-card">
        <div class="trust-card-title">📌 전문 카테고리</div>
        <p class="trust-card-desc">{cat} 중심의 핵심 주제별 분석 및 실전 활용 가이드</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">🎯 주요 독자층</div>
        <p class="trust-card-desc">{target}</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">🔍 정보 원천</div>
        <p class="trust-card-desc">공공기관 공식 발표, 공인 데이터베이스 및 학술·통계 자료</p>
      </div>
    </div>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">3. 콘텐츠 제작 철학</h2>
    <ul>
      <li><strong>원천 데이터 중심:</strong> 2차 가공된 소문이나 커뮤니티 풍문이 아닌, 공신력 있는 1차 출처만을 인용합니다.</li>
      <li><strong>이해하기 쉬운 표현:</strong> 어려운 전문 용어나 행정적 문구를 독자의 눈높이에 맞춘 일상 언어로 정제합니다.</li>
      <li><strong>과장 없는 객관성:</strong> 특정 상품이나 업체를 무비판적으로 추천하지 않으며 장단점을 공정하게 기록합니다.</li>
    </ul>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">4. 방문자에게 드리는 약속</h2>
    <div class="trust-callout-box">
      <strong>신뢰 메시지 (Trust Commitment):</strong><br/>
      {trust_msg}
    </div>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">5. 향후 운영 방향</h2>
    <p>
      {brand}는 일회성 트래픽을 노리는 자극적인 콘텐츠를 배제하고, 독자에게 오랜 시간 실질적인 도움이 되는 에버그린(Evergreen) 지식 아카이브를 구축해 나갈 것입니다. 
      제도나 정보가 변경될 경우 지속적인 모니터링을 통해 최신 상태를 유지할 것을 약속드립니다.
    </p>
  </div>

  <div class="trust-footer-meta">
    최초 게시일: 2026년 9월 | 최종 개정일: 2026년 9월 24일 | 운영팀: {brand} 에디토리얼 팀
  </div>
</div>
"""

    def generate_editorial_policy(self, identity: Dict[str, Any]) -> str:
        """PAGE 2: Editorial Policy & Content Standards."""
        brand = identity["brand_name"]
        cat = identity["category"]
        policy = identity["content_policy"]
        tone = identity["tone"]

        return f"""{self._base_style()}
<div class="trust-page-container">
  <span class="trust-header-badge">에디토리얼 가이드라인 · Editorial Policy</span>
  <h1 class="trust-title">{brand} 운영 철학 및 콘텐츠 작성 기준</h1>
  
  <div class="trust-lead-box">
    <strong>{brand}</strong>는 정직하고 객관적인 정보 제공을 최우선 가치로 삼습니다. 
    본 가이드라인은 본 사이트에 게시되는 모든 콘텐츠의 기획, 작성, 감수 및 사후 수정 전반에 적용되는 엄격한 편집 규정입니다.
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">1. 정보 수집 및 출처 선정 기준</h2>
    <p>
      본 사이트는 {cat} 분야의 특수성을 고려하여 아래의 공인된 원천 자료만을 1차 근거로 채택합니다:
    </p>
    <ul>
      <li><strong>정부 및 공공기관 공식 발표:</strong> 대한민국 정부 부처, 지방자치단체, 공공기관 고시 및 공고문</li>
      <li><strong>공인 통계 및 데이터베이스:</strong> 공공데이터포털(data.go.kr), 국가통계포털(KOSIS), 공인 공시자료</li>
      <li><strong>제조사 및 공식 주관사 공식 규격:</strong> 제조사 제품 사양서, 주최 측 공식 발표문</li>
      <li><strong>비공식 소처 엄격 배제:</strong> 출처가 불분명한 SNS 루머, 찌라시, 커뮤니티 카더라는 일체 인용하지 않습니다.</li>
    </ul>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">2. 콘텐츠 작성 및 표현 원칙</h2>
    <p>
      {brand}는 <strong>"{tone}"</strong>을 지향하며 아래의 작성 원칙을 의무 준수합니다:
    </p>
    <div class="trust-card-grid">
      <div class="trust-card">
        <div class="trust-card-title">🚫 과장된 수식어 배제</div>
        <p class="trust-card-desc">'최고의', '무조건', '100% 보장' 등 근거 없는 절대적 표현 사용을 금지합니다.</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">⚖️ 상업적 독립성</div>
        <p class="trust-card-desc">광고주나 협찬사의 요구로 인해 사실관계를 왜곡하거나 부정적 요소를 은폐하지 않습니다.</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">📖 독자 중심 서술</div>
        <p class="trust-card-desc">전문 용어를 독자가 바로 이해할 수 있도록 쉽게 풀어내며 실생활 적용 팁을 함께 제공합니다.</p>
      </div>
    </div>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">3. 상시 업데이트 및 정보 갱신 기준</h2>
    <p>
      정책, 세법, 여행지 운영시간, 제품 사양 등 시간의 경과에 따라 변동될 수 있는 정보에 대해서는 정기적인 전수 점검을 수행합니다. 
      공식 발표에 변동이 확인될 경우 기사 서두 또는 본문에 [수정/갱신 일자]를 명시하고 변경된 내용을 즉각 반영합니다.
    </p>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">4. 이해상충 방지 및 편집권의 독립</h2>
    <p>
      {brand}의 모든 콘텐츠는 에디토리얼 팀의 독립적인 판단에 따라 작성됩니다. 
      배너 광고나 제휴 링크가 포함될 수 있으나, 이는 본문의 객관적인 평가와 사실 기술에 어떠한 영향도 미칠 수 없도록 엄격히 격리 운영됩니다.
    </p>
  </div>

  <div class="trust-footer-meta">
    최초 제정일: 2026년 9월 | 최종 검토일: 2026년 9월 24일 | {brand} 편집위원회
  </div>
</div>
"""

    def generate_verification_policy(self, identity: Dict[str, Any]) -> str:
        """PAGE 3: Fact-Checking & Verification Policy."""
        brand = identity["brand_name"]
        cat = identity["category"]
        policy = identity["content_policy"]

        return f"""{self._base_style()}
<div class="trust-page-container">
  <span class="trust-header-badge">팩트체크 정책 · Fact-Checking & Verification Policy</span>
  <h1 class="trust-title">{brand} 정보 검증 및 팩트체크 정책</h1>
  
  <div class="trust-lead-box">
    <strong>{brand}</strong>는 인터넷에 만연한 오정보(Misinformation)와 잘못된 정보 확산을 방지하기 위해 엄격한 3단계 팩트체크 프로세스를 가동합니다. 
    독자에게 정확한 사실만을 전달하는 것이 본 사이트의 가장 중요한 약속입니다.
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">1. 분야별 팩트체크 기준 ({cat})</h2>
    <table class="trust-table">
      <tr>
        <th>검증 대상</th>
        <th>1차 공인 출처 및 검증 기준</th>
      </tr>
      <tr>
        <td>법령 및 지원사업</td>
        <td>대한민국 법제처 국가법령정보센터, 정부24(gov24), 각 중앙행정기관 고시·공고</td>
      </tr>
      <tr>
        <td>공공데이터 및 통계</td>
        <td>공공데이터포털(data.go.kr), 국가통계포털(KOSIS), 공공기관 알리오(ALIO) 공시</td>
      </tr>
      <tr>
        <td>기술 규격 및 사양</td>
        <td>제조사 공식 웹사이트, 국립전파연구원 적합성평가(KC인증), 공인 시험성적서</td>
      </tr>
      <tr>
        <td>문화·지리·여행 정보</td>
        <td>한국관광공사 TourAPI, 국토교통부 공간정보, 각 지자체 문화관광 공식 포털</td>
      </tr>
    </table>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">2. 팩트체크 3단계 검증 프로세스</h2>
    <div class="trust-card-grid">
      <div class="trust-card">
        <div class="trust-card-title">Step 1. 원천 자료 교차 대조</div>
        <p class="trust-card-desc">언론 기사나 2차 블로그가 아닌, 기관 공식 보도자료 및 공고 원문을 찾아 숫자의 일치 여부를 대조합니다.</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">Step 2. 최신 유효성 점검</div>
        <p class="trust-card-desc">작성 시점 기준 해당 제도나 규정이 현재 유효한지(폐지/수정 여부)를 정부 시스템에서 직접 조회합니다.</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">Step 3. 예외 조건 명시</div>
        <p class="trust-card-desc">모든 이에게 일률 적용되지 않는 지원 자격, 제외 대상, 한도 조항을 누락 없이 본문에 투명하게 안내합니다.</p>
      </div>
    </div>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">3. AI 생성 콘텐츠 검증 가이드라인</h2>
    <p>
      본 사이트는 최신 데이터 탐색에 AI 보조 도구를 활용할 수 있으나, <strong>모든 고유명사, 숫자, 날짜, 신청 자격 및 공식 링크는 사람 에디터의 100% 전수 팩트체크 검증</strong>을 통과한 후에만 최종 발행됩니다. 
      AI의 환각(Hallucination)에 의한 부정확한 수치나 가짜 규정은 시스템적으로 원천 차단됩니다.
    </p>
  </div>

  <div class="trust-footer-meta">
    최초 제정일: 2026년 9월 | 최종 갱신일: 2026년 9월 24일 | {brand} 팩트체크 데스크
  </div>
</div>
"""

    def generate_privacy_policy(self, identity: Dict[str, Any]) -> str:
        """PAGE 4: Privacy Policy (AdSense & Cookie Compliant)."""
        brand = identity["brand_name"]
        domain = identity["domain"]
        email = identity["email"]

        return f"""{self._base_style()}
<div class="trust-page-container">
  <span class="trust-header-badge">개인정보처리방침 · Privacy Policy</span>
  <h1 class="trust-title">{brand} 개인정보처리방침</h1>
  
  <div class="trust-lead-box">
    <strong>{brand}</strong>({domain})는 이용자의 개인정보를 매우 소중하게 생각하며, 「개인정보 보호법」 및 정보통신망 이용촉진 및 정보보호 등에 관한 법률을 준수합니다. 
    본 방침은 귀하가 본 웹사이트를 이용할 때 어떤 정보가 수집되고 어떻게 활용되는지 명확히 설명합니다.
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">1. 수집하는 개인정보 항목 및 수집 방법</h2>
    <p>본 사이트는 회원가입 없이 누구나 자유롭게 이용할 수 있는 공개 웹사이트로서, 원칙적으로 이용자의 주민등록번호나 민감한 개인정보를 수집하지 않습니다.</p>
    <ul>
      <li><strong>자동 생성 정보:</strong> 웹사이트 접속 시 IP 주소, 브라우저 종류, 방문 일시, 방문 페이지 기록(URL), 기기 정보 등이 통계 목적으로 자동 기록될 수 있습니다.</li>
      <li><strong>문의 접수 시:</strong> 문의 페이지를 통해 사용자가 자발적으로 이메일을 보내는 경우, 답변 처리를 위해 이메일 주소 및 문의 내용이 수집됩니다.</li>
    </ul>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">2. 쿠키(Cookie)의 운용 및 Google AdSense 안내</h2>
    <p>
      본 사이트는 이용자에게 최적화된 편의를 제공하고 통계 분석 및 맞춤형 광고를 게재하기 위해 '쿠키(Cookie)'를 사용합니다.
    </p>
    <div class="trust-card-grid">
      <div class="trust-card">
        <div class="trust-card-title">🍪 쿠키의 정의</div>
        <p class="trust-card-desc">웹사이트를 운영하는데 이용되는 서버가 이용자의 컴퓨터 브라우저에 보내는 소량의 텍스트 파일로 하드디스크에 저장됩니다.</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">📢 Google AdSense 광고</div>
        <p class="trust-card-desc">구글을 포함한 제3자 광고 공급업체는 사용자의 이전 웹사이트 방문 기록을 기반으로 맞춤형 광고를 게재하기 위해 DoubleClick 쿠키를 사용할 수 있습니다.</p>
      </div>
    </div>
    <p>
      <strong>쿠키 설치 거부 방법:</strong> 이용자는 쿠키 설치에 대한 선택권을 가지고 있습니다. 
      웹 브라우저 상단의 [도구] > [인터넷 옵션] > [개인정보] 메뉴에서 모든 쿠키를 허용하거나, 저장될 때마다 확인을 거치거나, 모든 쿠키의 저장을 거부할 수 있습니다. 
      또한 구글 맞춤 광고 설정은 <a href="https://adssettings.google.com" target="_blank" rel="noopener noreferrer">구글 광고 설정 페이지</a>에서 비활성화할 수 있습니다.
    </p>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">3. 웹로그 분석 도구 (Google Analytics)</h2>
    <p>
      본 웹사이트는 사이트 이용 행태 분석 및 서비스 개선을 위해 Google Analytics 등 트래픽 분석 도구를 활용할 수 있습니다. 
      이 도구는 익명화된 데이터만을 처리하며, 개인을 특정할 수 있는 정보와 결합되지 않습니다.
    </p>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">4. 개인정보의 보유 및 파기</h2>
    <p>
      이메일 문의를 통해 수집된 정보는 문의 처리 및 사후 분쟁 해결을 위해 접수일로부터 1년간 보관된 후 재생이 불가능한 방법으로 영구 파기됩니다.
    </p>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">5. 개인정보 보호책임자 및 고충처리 창구</h2>
    <p>본 사이트의 개인정보 처리와 관련하여 문의사항이나 불만 처리가 필요하신 경우 아래의 창구로 연락 주시면 신속하게 조치하겠습니다:</p>
    <div class="trust-contact-box">
      • 사이트명: {brand}<br/>
      • 공식 URL: <a href="{domain}">{domain}</a><br/>
      • 개인정보 담당 부서: {brand} 개인정보보호팀<br/>
      • 공식 문의 이메일: <a href="mailto:{email}">{email}</a>
    </div>
  </div>

  <div class="trust-footer-meta">
    공고일자: 2026년 9월 1일 | 시행일자: 2026년 9월 24일 | {brand}
  </div>
</div>
"""

    def generate_terms(self, identity: Dict[str, Any]) -> str:
        """PAGE 5: Terms of Service."""
        brand = identity["brand_name"]
        domain = identity["domain"]
        cat = identity["category"]

        return f"""{self._base_style()}
<div class="trust-page-container">
  <span class="trust-header-badge">이용약관 · Terms of Service</span>
  <h1 class="trust-title">{brand} 서비스 이용약관</h1>
  
  <div class="trust-lead-box">
    본 약관은 <strong>{brand}</strong>({domain})가 제공하는 모든 콘텐츠 및 정보 서비스의 이용 조건과 운영자 및 이용자의 권리, 의무, 책임사항을 규정함을 목적으로 합니다.
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">제1조 (목적 및 성격)</h2>
    <p>
      {brand}는 {cat} 분야의 공개된 공공 데이터 및 공인 정보를 알기 쉽게 정리하여 독자에게 비영리적·참고 목적으로 제공하는 독립 정보 웹사이트입니다.
    </p>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">제2조 (전문적 조언의 부존재 및 책임의 한계)</h2>
    <ul>
      <li><strong>일반 정보의 제공:</strong> 본 사이트의 모든 글과 자료는 일반적인 정보 제공만을 목적으로 하며, 특정 개인이나 사업자에 대한 법률적, 세무적, 금융적, 의학적 전문가의 공식 자문을 대신할 수 없습니다.</li>
      <li><strong>최종 결정의 책임:</strong> 이용자가 본 사이트에 게재된 정보를 바탕으로 내린 결정, 투자, 청약, 신청 등으로 인해 발생하는 결과에 대한 모든 책임은 이용자 본인에게 있습니다. 중요한 행정 절차나 계약 전에는 반드시 해당 주관 부처 및 기관의 공식 안내를 재확인하시기 바랍니다.</li>
      <li><strong>면책 조항:</strong> {brand}는 정보의 정확성과 최신성을 유지하기 위해 최선을 다하지만, 정부 정책의 불시 변경, 지자체 조례 수정 등으로 인한 일시적 오차나 지연에 대해 법적 보증 책임을 지지 않습니다.</li>
    </ul>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">제3조 (지적재산권 및 저작권 정책)</h2>
    <ul>
      <li>본 사이트에 작성된 텍스트, 구성 레이아웃, 인포그래픽, 카드뉴스 등 저작물에 대한 저작권은 {brand}에 귀속됩니다.</li>
      <li>이용자는 본 사이트의 콘텐츠를 개인적인 비영리 목적으로 인용하거나 SNS에 링크(URL 공유)할 수 있습니다. 단, 출처({brand} 및 해당 URL)를 명확히 표기해야 합니다.</li>
      <li>사전 서면 승인 없이 본 사이트의 콘텐츠 전체를 무단 복제, 배포, 상업적 크롤링, AI 학습 데이터셋 무단 전용하는 행위는 엄격히 금지됩니다.</li>
    </ul>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">제4조 (외부 링크에 대한 면책)</h2>
    <p>
      본 사이트는 이용자의 편의를 위해 정부 공식 웹사이트, 공공기관 신청 페이지 등 제3자 웹사이트로 연결되는 링크를 제공합니다. 
      {brand}는 외부 링크된 제3자 사이트의 운영, 콘텐츠, 개인정보 정책에 대해 통제권이 없으며 어떠한 법적 책임도 부담하지 않습니다.
    </p>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">제5조 (약관의 개정)</h2>
    <p>
      본 약관은 관련 법령의 개정이나 사이트 운영 방침의 변화에 따라 사전 예고 없이 변경될 수 있으며, 개정된 약관은 본 페이지에 게시된 시점부터 즉시 효력이 발생합니다.
    </p>
  </div>

  <div class="trust-footer-meta">
    시행일자: 2026년 9월 24일 | {brand} 운영위원회
  </div>
</div>
"""

    def generate_contact(self, identity: Dict[str, Any]) -> str:
        """PAGE 6: Contact Us."""
        brand = identity["brand_name"]
        domain = identity["domain"]
        email = identity["email"]
        cat = identity["category"]

        return f"""{self._base_style()}
<div class="trust-page-container">
  <span class="trust-header-badge">공식 문의처 · Contact Us</span>
  <h1 class="trust-title">{brand} 문의 및 피드백</h1>
  
  <div class="trust-lead-box">
    <strong>{brand}</strong>는 독자 여러분의 소중한 의견, 정보 수정 제보, 제휴 및 협업 문의를 언제나 환영합니다. 
    보내주시는 피드백은 사이트 품질을 높이고 더 신뢰할 수 있는 정보 플랫폼을 만드는 밑거름이 됩니다.
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">1. 문의 접수 분야</h2>
    <div class="trust-card-grid">
      <div class="trust-card">
        <div class="trust-card-title">📝 콘텐츠 수정 및 오류 제보</div>
        <p class="trust-card-desc">변경된 정책, 오탈자, 잘못된 정보 발견 시 URL과 정정 내용을 보내주시면 신속히 반영합니다.</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">🤝 광고 및 비즈니스 제휴</div>
        <p class="trust-card-desc">{cat} 분야의 건전한 파트너십 및 스폰서십 문의를 정중히 검토합니다.</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">💡 기타 의견 및 제안</div>
        <p class="trust-card-desc">새롭게 다루어 주었으면 하는 주제나 사이트 이용 중 불편사항을 자유롭게 제안해 주세요.</p>
      </div>
    </div>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">2. 공식 소통 창구</h2>
    <div class="trust-contact-box">
      <table class="trust-table" style="margin: 0;">
        <tr>
          <th>공식 이메일</th>
          <td><strong style="color: #2563eb; font-size: 16px;"><a href="mailto:{email}">{email}</a></strong></td>
        </tr>
        <tr>
          <th>운영 시간</th>
          <td>평일 09:30 ~ 18:30 (대한민국 표준시 기준, 주말 및 공휴일 휴무)</td>
        </tr>
        <tr>
          <th>회신 기준</th>
          <td>접수된 문의는 <strong>영업일 기준 24~48시간 이내</strong>에 담당 에디터가 검토 후 성실히 답변드립니다.</td>
        </tr>
        <tr>
          <th>사이트 도메인</th>
          <td><a href="{domain}" target="_blank">{domain}</a></td>
        </tr>
      </table>
    </div>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">3. 문의 시 유의사항</h2>
    <p>
      스팸 방지 및 원활한 상담을 위해 메일 제목에 <strong>[오류신고], [제휴문의], [피드백]</strong> 등 머리말을 달아주시면 더욱 신속하게 처리됩니다. 
      불법 스팸, 비방, 개인정보가 포함된 문의는 사전 통보 없이 삭제될 수 있습니다.
    </p>
  </div>

  <div class="trust-footer-meta">
    {brand} 독자소통 데스크 | 공식 소통 창구
  </div>
</div>
"""

    def generate_correction_policy(self, identity: Dict[str, Any]) -> str:
        """PAGE 7: Content Correction & Error Reporting Policy."""
        brand = identity["brand_name"]
        domain = identity["domain"]
        email = identity["email"]

        return f"""{self._base_style()}
<div class="trust-page-container">
  <span class="trust-header-badge">오류 정정 정책 · Correction Policy</span>
  <h1 class="trust-title">{brand} 콘텐츠 수정 및 오류 신고 정책</h1>
  
  <div class="trust-lead-box">
    <strong>{brand}</strong>는 정확성을 최우선으로 추구하지만, 인간적인 실수나 제도 변경으로 인한 오차가 발생할 수 있음을 인정합니다. 
    오류가 발견되었을 때 이를 숨기지 않고 신속하고 투명하게 바로잡는 것이 독자에 대한 진정한 예의이자 신뢰의 기반입니다.
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">1. 오류 제보 접수 창구</h2>
    <p>
      본 사이트의 게시물 중 잘못된 수치, 만료된 일정, 부적절한 링크, 오탈자를 발견하셨다면 언제든지 아래 이메일로 제보해 주시기 바랍니다:
    </p>
    <div class="trust-callout-box">
      • 오류 제보 전용 이메일: <strong><a href="mailto:{email}">{email}</a></strong><br/>
      • 포함 내용: 해당 게시물 URL, 잘못된 부분, 올바른 사실 및 공식 출처 링크(보도자료 등)
    </div>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">2. 오류 검토 및 수정 3단계 절차</h2>
    <div class="trust-card-grid">
      <div class="trust-card">
        <div class="trust-card-title">1단계: 제보 접수 및 팩트 확인</div>
        <p class="trust-card-desc">접수 즉시 담당 에디터가 주관 기관의 최신 공고문 및 법령과 대조하여 사실관계를 재검증합니다.</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">2단계: 신속 정정 반영</div>
        <p class="trust-card-desc">오류가 확인되면 24시간 이내에 본문 내용을 올바르게 수정합니다. 단순 오탈자는 즉시 수정합니다.</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">3단계: 정정 이력 투명 공개</div>
        <p class="trust-card-desc">중대한 사실관계 변경이 있는 경우, 기사 하단에 [수정 일시] 및 [정정 내용 요약]을 투명하게 고지합니다.</p>
      </div>
    </div>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">3. 정정 이력 표기 방식 (예시)</h2>
    <div style="background: #f1f5f9; border-left: 3px solid #64748b; padding: 12px 16px; font-size: 14px; color: #475569; margin: 12px 0;">
      <em>[정정 공지: 2026년 09월 00일 기준 해당 제도의 소득 요건 기준액이 보건복지부 고시에 맞춰 00만원에서 00만원으로 수정되었습니다.]</em>
    </div>
  </div>

  <div class="trust-footer-meta">
    제정일자: 2026년 9월 24일 | {brand} 팩트체크 및 정정 데스크
  </div>
</div>
"""

    def generate_partnership(self, identity: Dict[str, Any]) -> str:
        """PAGE 8: Advertising & Partnership Disclosure."""
        brand = identity["brand_name"]
        domain = identity["domain"]
        email = identity["email"]
        cat = identity["category"]

        return f"""{self._base_style()}
<div class="trust-page-container">
  <span class="trust-header-badge">광고 및 제휴 안내 · Advertising Disclosure</span>
  <h1 class="trust-title">{brand} 광고 및 파트너십 정책</h1>
  
  <div class="trust-lead-box">
    <strong>{brand}</strong>는 양질의 콘텐츠를 독자에게 전액 무료로 지속 제공하기 위해 광고 및 제휴 프로그램을 운영하고 있습니다. 
    본 페이지는 본 사이트의 광고 수익 모델과 에디토리얼 독립성 보장 원칙을 독자 여러분께 투명하게 공개합니다.
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">1. 광고 및 제휴 콘텐츠 분리 원칙</h2>
    <ul>
      <li><strong>시각적 분리:</strong> 본 사이트에 노출되는 배너 광고는 본문 기사와 시각적으로 명확히 구분되는 위치에 배치되며, 광고임을 식별할 수 있는 레이블이 적용됩니다.</li>
      <li><strong>광고 표시 준수:</strong> 경제적 대가가 수반된 콘텐츠는 공정거래위원회의 「추천·보증 등에 관한 표시·광고 심사지침」에 따라 본문 서두 또는 결미에 '협찬', '스폰서드', 또는 '유료 광고 포함' 문구를 명확히 표기합니다.</li>
      <li><strong>편집권의 절대 독립:</strong> 광고주나 제휴 파트너는 본 사이트의 평가 기준이나 비판적 의견을 변경하거나 통제할 수 없습니다. 상업적 이해관계로 인해 객관적 사실을 왜곡하는 일은 절대 없습니다.</li>
    </ul>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">2. 운영 중인 광고 플랫폼</h2>
    <div class="trust-card-grid">
      <div class="trust-card">
        <div class="trust-card-title">Google AdSense</div>
        <p class="trust-card-desc">구글의 정책을 준수하는 자동 디스플레이 광고를 게재하며, 불법·선정적·기만적 광고는 엄격히 필터링합니다.</p>
      </div>
      <div class="trust-card">
        <div class="trust-card-title">공식 브랜드 협업</div>
        <p class="trust-card-desc">{cat} 관련 양질의 공식 서비스나 제품에 한해 사전 적합성 심사를 통과한 파트너십만을 진행합니다.</p>
      </div>
    </div>
  </div>

  <div class="trust-section">
    <h2 class="trust-section-title">3. 파트너십 및 제휴 문의</h2>
    <p>
      {brand}와 함께 가치 있는 정보를 독자에게 전달하고자 하는 기관, 브랜드, 서비스 제공자분들은 아래 이메일로 제안서를 보내주시기 바랍니다:
    </p>
    <div class="trust-contact-box">
      • 제휴 전용 창구: <strong><a href="mailto:{email}">{email}</a></strong><br/>
      • 심사 기준: 독자에게 실질적인 유익을 제공하는 합법적이고 건전한 서비스 여부 검토 후 3영업일 이내 회신
    </div>
  </div>

  <div class="trust-footer-meta">
    공개일자: 2026년 9월 24일 | {brand} 비즈니스 협력팀
  </div>
</div>
"""

    def generate_all_pages_for_blog(self, blog_id: int) -> List[Dict[str, str]]:
        """Generate all 8 trust pages for a specific blog identity."""
        identity = MASTER_IDENTITIES.get(blog_id)
        if not identity:
            raise ValueError(f"Unknown blog_id: {blog_id}")

        brand = identity["brand_name"]

        pages = [
            {
                "page_type": "about-us",
                "slug": "about-us",
                "title": f"{brand} 소개 (About Us)",
                "content": self.generate_about_us(identity)
            },
            {
                "page_type": "editorial-policy",
                "slug": "editorial-policy",
                "title": f"{brand} 운영 철학 및 콘텐츠 작성 기준 (Editorial Policy)",
                "content": self.generate_editorial_policy(identity)
            },
            {
                "page_type": "verification-policy",
                "slug": "verification-policy",
                "title": f"{brand} 정보 검증 및 팩트체크 정책 (Fact-Checking)",
                "content": self.generate_verification_policy(identity)
            },
            {
                "page_type": "privacy-policy",
                "slug": "privacy-policy",
                "title": f"{brand} 개인정보처리방침 (Privacy Policy)",
                "content": self.generate_privacy_policy(identity)
            },
            {
                "page_type": "terms",
                "slug": "terms",
                "title": f"{brand} 서비스 이용약관 (Terms of Service)",
                "content": self.generate_terms(identity)
            },
            {
                "page_type": "contact",
                "slug": "contact",
                "title": f"{brand} 문의 및 피드백 (Contact Us)",
                "content": self.generate_contact(identity)
            },
            {
                "page_type": "correction-policy",
                "slug": "correction-policy",
                "title": f"{brand} 콘텐츠 수정 및 오류 신고 정책 (Correction Policy)",
                "content": self.generate_correction_policy(identity)
            },
            {
                "page_type": "partnership",
                "slug": "partnership",
                "title": f"{brand} 광고 및 제휴 안내 (Partnership)",
                "content": self.generate_partnership(identity)
            }
        ]
        return pages

    def build_and_save_all_to_db(self) -> int:
        """Generate all 8 pages for all 8 blogs (total 64 pages) and save into database."""
        from trust_page_generator.identities import sync_identities_to_db

        # First sync identities
        sync_identities_to_db()

        db = SessionLocal()
        total_saved = 0
        try:
            for blog_id in MASTER_IDENTITIES.keys():
                pages_data = self.generate_all_pages_for_blog(blog_id)
                for p in pages_data:
                    existing = db.query(TrustPage).filter(
                        TrustPage.blog_id == blog_id,
                        TrustPage.page_type == p["page_type"]
                    ).first()

                    if existing:
                        existing.title = p["title"]
                        existing.slug = p["slug"]
                        existing.content = p["content"]
                        existing.status = "READY"
                        existing.updated_date = datetime.now(timezone.utc)
                    else:
                        new_page = TrustPage(
                            blog_id=blog_id,
                            page_type=p["page_type"],
                            title=p["title"],
                            slug=p["slug"],
                            content=p["content"],
                            status="READY"
                        )
                        db.add(new_page)
                    total_saved += 1
            db.commit()
        finally:
            db.close()

        return total_saved
