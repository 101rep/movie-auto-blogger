"""Tests for Phase 4: AI Fact Checker."""
import pytest
from app.ai.schemas import ArticleOutput, FAQItem
from app.database.models import Movie, QualityStatusEnum
from app.services.fact_check_service import (
    ClaimType,
    FactCheckService,
    FactCheckStatus,
)
from app.services.quality_service import QualityGateService


def create_sample_article(
    title: str = "영화 인셉션 완벽 분석: 크리스토퍼 놀란의 걸작",
    director_text: str = "크리스토퍼 놀란 감독이 연출하고",
    year_text: str = "2010년 개봉하여 전 세계적인 찬사를 받은 작품입니다.",
    runtime_text: str = "상영시간 148분 동안 팽팽한 긴장감을 유지합니다.",
    cast_text: str = "레오나르도 디카프리오, 조셉 고든 레빗 등이 열연을 펼쳤습니다.",
    director_faq_name: str = "크리스토퍼 놀란"
) -> ArticleOutput:
    """Helper creating a complete valid ArticleOutput with >600 chars for testing."""
    intro = (
        f"영화 인셉션은 꿈 속의 꿈을 다룬 SF 명작입니다. {year_text} "
        "꿈과 무의식의 세계를 치밀하게 설계하여 관객들에게 전례 없는 시각적 충격과 "
        "지적인 지적 유희를 동시에 선사하는 현대 영화사의 기념비적인 역작으로 손꼽힙니다."
    )
    basic = (
        f"영화 인셉션의 기본정보: {director_text} {runtime_text} 명작의 반열에 올랐습니다. "
        "영화의 시각효과와 정교한 음향 설계는 영화관을 가득 채우며 완벽한 몰입감을 선사합니다. "
        "시간의 왜곡과 공간의 붕괴를 다룬 혁신적인 비주얼이 돋보입니다."
    )
    synopsis = (
        "타인의 꿈에 들어가 생각을 훔치는 특수 보안 요원 코브의 이야기입니다. "
        "기업의 거대한 비밀을 빼내는 추출 작업을 전문으로 하던 그는 마지막 미션으로 생각을 훔치는 것이 아닌 "
        "타인의 무의식에 새로운 생각을 심는 위험천만한 인셉션을 제안받고 각 분야의 전문가들을 모아 팀을 꾸립니다."
    )
    cast = (
        f"{cast_text} {director_text} 뛰어난 연출력을 발휘하며 배우들의 밀도 높은 연기가 어우러집니다. "
        "특히 주인공 코브 역을 맡은 배우의 내면적 고뇌와 슬픔이 정교하게 묘사되어 극의 깊이를 더해줍니다."
    )
    conclusion = (
        "영화 인셉션은 생각의 힘과 현실의 경계에 대해 오랜 시간 깊은 여운을 남깁니다. "
        "엔딩 크레딧이 올라갈 때까지 회전하는 토템 팽이의 마지막 장면은 관객들에게 현실과 무의식의 본질에 대한 "
        "영원히 풀리지 않는 철학적 질문을 던지며 수많은 해석을 낳고 있습니다."
    )

    return ArticleOutput(
        title=title,
        excerpt="영화 인셉션의 줄거리와 관람 포인트, 결말 해석 및 자주 묻는 질문 총정리 완벽 가이드입니다.",
        slug_hint="inception-review",
        introduction=intro,
        basic_info_summary=basic,
        spoiler_free_synopsis=synopsis,
        cast_and_director=cast,
        viewing_points=["정교한 꿈의 계층 구조와 무중력 격투신", "한스 짐머의 웅장하고 긴장감 넘치는 OST"],
        recommended_for=["치밀한 플롯의 SF 영화 매니아", "열린 결말과 해석을 좋아하는 관객"],
        similar_movie_notes=["인터스텔라", "매트릭스", "셔터 아일랜드"],
        faq=[
            FAQItem(
                question="인셉션 엔딩의 팽이는 멈췄나요?",
                answer=f"{director_faq_name} 감독은 현실과 꿈의 경계보다 코브가 마침내 아이들과 재회하는 감정적 해방이 가장 중요하다고 밝혔습니다."
            )
        ],
        conclusion=conclusion,
        seo_title="영화 인셉션 줄거리 결말 해석 평점 총정리",
        meta_description="영화 인셉션의 기본정보, 줄거리와 출연진, 결말 해석 및 자주 묻는 질문까지 한눈에 알아보는 완벽 가이드.",
        tags=["인셉션", "크리스토퍼놀란", "SF영화"]
    )


def test_fact_check_verified_match():
    """Verify correct claims are marked as VERIFIED."""
    movie = Movie(
        id=1,
        title="인셉션",
        director="크리스토퍼 놀란",
        release_date="2010-07-21",
        runtime=148,
        cast_json='["레오나르도 디카프리오", "조셉 고든 레빗", "마리옹 꼬띠아르"]'
    )
    article = create_sample_article()
    report = FactCheckService.extract_and_verify(article, movie)

    assert report.conflict_count == 0
    assert report.has_fatal_conflict is False
    assert report.verified_count >= 3

    title_item = next(i for i in report.items if i.claim_type == ClaimType.TITLE)
    assert title_item.status == FactCheckStatus.VERIFIED

    director_item = next(i for i in report.items if i.claim_type == ClaimType.DIRECTOR)
    assert director_item.status == FactCheckStatus.VERIFIED


def test_fact_check_director_conflict():
    """Verify hallucinated or incorrect director triggers CONFLICT and fatal flag."""
    movie = Movie(
        id=2,
        title="인셉션",
        director="크리스토퍼 놀란",
        release_date="2010-07-21",
        runtime=148
    )
    # Article claims Bong Joon-ho is the director without mentioning Christopher Nolan
    article = create_sample_article(
        title="영화 인셉션 완벽 분석: 봉준호 감독의 걸작",
        director_text="봉준호 감독이 연출하여 독창적인 긴장감을 부여하고",
        director_faq_name="봉준호"
    )
    report = FactCheckService.extract_and_verify(article, movie)

    assert report.conflict_count >= 1
    assert report.has_fatal_conflict is True
    director_item = next(i for i in report.items if i.claim_type == ClaimType.DIRECTOR)
    assert director_item.status == FactCheckStatus.CONFLICT


def test_fact_check_runtime_severe_conflict():
    """Verify severe discrepancy in runtime triggers CONFLICT."""
    movie = Movie(
        id=3,
        title="인셉션",
        director="크리스토퍼 놀란",
        release_date="2010-07-21",
        runtime=148
    )
    # Mentions 210 minutes (62 minutes diff)
    article = create_sample_article(
        runtime_text="상영시간 210분 동안 긴장감이 이어집니다."
    )
    report = FactCheckService.extract_and_verify(article, movie)

    runtime_item = next((i for i in report.items if i.claim_type == ClaimType.RUNTIME), None)
    assert runtime_item is not None
    assert runtime_item.status == FactCheckStatus.CONFLICT


def test_quality_gate_integration_with_fact_check():
    """Verify QualityGate integrates fact check results into PASS/FAIL decisions."""
    movie = Movie(
        id=4,
        title="인셉션",
        director="크리스토퍼 놀란",
        release_date="2010-07-21",
        runtime=148
    )

    # 1. Matching article -> PASS (>600 chars, no conflicts)
    good_article = create_sample_article()
    status, issues = QualityGateService.evaluate(good_article, expected_movie_title="인셉션", movie=movie)
    assert status == QualityStatusEnum.PASS
    assert len(issues) == 0

    # 2. Fatal conflict article (Wrong Director) -> FAIL
    bad_article = create_sample_article(
        title="영화 인셉션 완벽 분석: 스티븐 스필버그의 작품",
        director_text="스티븐 스필버그 감독이 연출한 블록버스터로",
        director_faq_name="스티븐 스필버그"
    )
    bad_status, bad_issues = QualityGateService.evaluate(bad_article, expected_movie_title="인셉션", movie=movie)
    assert bad_status == QualityStatusEnum.FAIL
    assert any("치명적 팩트 불일치" in issue for issue in bad_issues)
