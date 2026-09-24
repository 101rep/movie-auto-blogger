"""Experience Engine orchestrating Deep Interview, Context Notebook, Outline, and Draft generation."""
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.ai.experience_schemas import (
    ContextEpisode,
    ContextNotebook,
    ExperienceDraft,
    ExperienceGroundingReport,
    ExperienceOutline,
    H2SectionOutline,
    InterviewSessionState,
    InterviewTurn,
)
from app.ai.router import AIProviderRouter
from app.core.prompts.registry import PromptRegistry
from app.core.quality.skill import CONTENT_QUALITY_VERSION, ContentQualitySkill
from app.database.models import InterviewSessionModel, Post, PostStatusEnum, QualityStatusEnum
from app.database.session import SessionLocal
from app.services.experience_grounding_service import ExperienceGroundingService
from app.utils.logging import get_logger
from app.utils.slug import generate_slug

logger = get_logger("experience_service")

# Generic responses requiring drill-down exploration
GENERIC_ANSWER_TRIGGERS = [
    "좋았습니다", "편했습니다", "가성비가 좋았습니다", "맛있었습니다",
    "위치가 좋았습니다", "추천합니다", "예뻤습니다", "괜찮았습니다",
    "만족스러웠습니다", "나쁘지 않았습니다", "좋았어요", "편했어요"
]


class ExperienceService:
    """Orchestrates Deep Interview sessions, Context Notebook memory, Outline, and Drafts."""

    def __init__(self, ai_router: Optional[AIProviderRouter] = None):
        self.router = ai_router or AIProviderRouter()
        self.quality_skill = ContentQualitySkill(profile_name="experience")

    def _get_db(self) -> Session:
        return SessionLocal()

    def start_interview(
        self,
        topic: str,
        main_keyword: Optional[str] = None
    ) -> Tuple[InterviewSessionState, str]:
        """Initialize an interview session, determine subtopics, and pose Question 1."""
        session_uuid = uuid.uuid4().hex[:16]
        clean_topic = topic.strip()
        derived_keyword = main_keyword.strip() if main_keyword else clean_topic.split()[0]

        subtopics = [
            f"{clean_topic} 실제 방문/사용 시 겪은 예상 밖의 시행착오",
            f"{clean_topic} 선택하기 전 치열하게 고민하고 비교한 대안",
            f"{clean_topic} 직접 겪어보고 나서야 비로소 알게 된 알짜배기 꿀팁"
        ]

        opening_question = (
            f"안녕하세요! '{clean_topic}'에 대한 진솔한 경험을 담아낼 수 있도록 취재를 시작하겠습니다. "
            f"먼저, 이번 경험을 결심하게 된 계기나 가장 처음 맞닥뜨렸던 인상적인 순간은 언제, 어떤 상황이었나요?"
        )

        state = InterviewSessionState(
            session_id=session_uuid,
            topic=clean_topic,
            main_keyword=derived_keyword,
            suggested_subtopics=subtopics,
            turns=[
                InterviewTurn(
                    round=1,
                    question=opening_question,
                    original_answer="",
                    extracted_episodes=[],
                    extracted_facts=[],
                    is_drilldown=False
                )
            ],
            context_notebook=ContextNotebook(
                topic=clean_topic,
                main_keyword=derived_keyword,
                interview_round=1
            ),
            status="IN_PROGRESS"
        )

        # Persist session to DB
        db = self._get_db()
        try:
            model = InterviewSessionModel(
                session_uuid=session_uuid,
                topic=clean_topic,
                main_keyword=derived_keyword,
                vertical="EXPERIENCE",
                status="IN_PROGRESS",
                current_round=1,
                turns_json=json.dumps([t.model_dump() for t in state.turns], ensure_ascii=False),
                context_notebook_json=state.context_notebook.model_dump_json()
            )
            db.add(model)
            db.commit()
        finally:
            db.close()

        logger.info("Experience interview session started: %s ('%s')", session_uuid, clean_topic)
        return state, opening_question

    def process_answer(
        self,
        session_uuid: str,
        user_answer: str
    ) -> Tuple[InterviewSessionState, str, bool]:
        """Process user answer, execute drill-down or extract episode, and advance interview.

        Returns:
            Tuple[state, next_question_or_completion_message, is_completed]
        """
        db = self._get_db()
        try:
            model = db.query(InterviewSessionModel).filter_by(session_uuid=session_uuid).first()
            if not model:
                raise ValueError(f"인터뷰 세션 '{session_uuid}'를 찾을 수 없습니다.")

            turns_data = json.loads(model.turns_json) if model.turns_json else []
            turns = [InterviewTurn.model_validate(t) for t in turns_data]
            notebook = ContextNotebook.model_validate_json(model.context_notebook_json) if model.context_notebook_json else ContextNotebook()

            current_turn = turns[-1] if turns else None
            answer_clean = user_answer.strip()

            # 1. Drill-down detection for generic answers
            is_generic = (
                len(answer_clean) < 30 and
                any(g in answer_clean for g in GENERIC_ANSWER_TRIGGERS)
            )

            if is_generic:
                # Drill-down: do NOT record episode, ask single specific follow-up
                drilldown_question = (
                    f"'{answer_clean}'라고 느끼셨던 구체적인 실제 상황 하나만 떠올려 주세요. "
                    f"예를 들어 짐을 옮겼던 순간이나 예상과 달랐던 순간처럼, 그것 때문에 일정이 크게 달라졌거나 당황했던 일이 있었나요?"
                )
                if current_turn:
                    current_turn.original_answer = answer_clean
                    current_turn.is_drilldown = True

                drill_turn = InterviewTurn(
                    round=model.current_round,
                    question=drilldown_question,
                    original_answer="",
                    extracted_episodes=[],
                    extracted_facts=[],
                    is_drilldown=True
                )
                turns.append(drill_turn)

                model.turns_json = json.dumps([t.model_dump() for t in turns], ensure_ascii=False)
                db.commit()

                state = InterviewSessionState(
                    session_id=session_uuid,
                    topic=model.topic,
                    main_keyword=model.main_keyword or "",
                    turns=turns,
                    context_notebook=notebook,
                    status=model.status
                )
                return state, drilldown_question, False

            # 2. Concrete Answer: Extract Episode & Numbers
            if current_turn:
                current_turn.original_answer = answer_clean

            # Extract numbers (currency, hours, days, percentages)
            extracted_numbers = re.findall(r'\b\d+(?:[.,]\d+)?(?:만원|원|달러|분|시간|박|일|%|km|m)?', answer_clean)
            extracted_numbers = [n for n in extracted_numbers if re.search(r'\d', n) and len(n) >= 2]

            # Generate structured episode
            ep_id = f"E{len(notebook.episodes) + 1:02d}"
            new_episode = ContextEpisode(
                id=ep_id,
                situation=answer_clean[:120],
                problem_or_conflict="예상과 다른 변수 발생" if any(w in answer_clean for w in ["하지만", "문제", "힘들", "걱정", "달랐"]) else "선택 및 실행",
                action=answer_clean,
                result="직접 해결 및 경험 확보",
                emotion="당황 및 안도" if any(w in answer_clean for w in ["놀랍", "당황", "걱정", "다행"]) else "만족",
                specific_numbers=extracted_numbers[:3],
                unique_observation="현장에서 직접 체득한 핵심 요점",
                source_type="user_interview",
                confidence="user_reported"
            )

            notebook.episodes.append(new_episode)
            notebook.facts.append(answer_clean)
            if extracted_numbers:
                notebook.numbers.extend(extracted_numbers)
                notebook.numbers = list(dict.fromkeys(notebook.numbers))

            if current_turn:
                current_turn.extracted_episodes.append(new_episode)
                current_turn.extracted_facts.append(answer_clean)

            # Check for photo mentions
            if any(p in answer_clean for p in ["사진", "촬영", "카메라", "찍었"]):
                notebook.photo_opportunities.append(f"에피소드 {ep_id} 관련 직접 촬영 사진")

            # Check for mistakes or regrets
            if any(m in answer_clean for m in ["후회", "아쉬", "실수", "바꾸고", "시행착오"]):
                notebook.mistakes.append(answer_clean)

            # Advance round
            model.current_round += 1
            notebook.interview_round = model.current_round

            # 3. Check Termination Condition: round >= 4 AND episodes >= 3 (or round >= 5)
            is_completed = (model.current_round >= 4 and len(notebook.episodes) >= 3) or model.current_round >= 5

            if is_completed:
                model.status = "COMPLETED"
                next_msg = (
                    f"🎉 충분한 실제 경험 취재가 완료되었습니다! (총 {len(notebook.episodes)}개 고유 에피소드 확보)\n"
                    f"취재 수첩(Context Notebook)을 바탕으로 '경험 기반 아웃라인 생성'을 진행할 수 있습니다."
                )
            else:
                # Dynamic next targeted question based on round
                questions_by_round = {
                    2: f"그 과정에서 예상치 못하게 겪었던 가장 큰 난관이나 당황스러웠던 문제점(시행착오)은 무엇이었나요?",
                    3: f"비슷한 다른 선택지(대안)와 비교했을 때, 왜 이 방식을 최종 선택하셨나요? 실제 소요된 비용이나 시간은 어떠셨나요?",
                    4: f"다시 그 순간으로 돌아간다면 꼭 바꾸고 싶은 부분이나, 처음 경험하는 분들에게 전하고 싶은 '나만의 팁'이 있다면 무엇인가요?",
                    5: f"직접 촬영해 둔 사진이나 남겨둔 메모/영수증 같은 생생한 기록물이 있으신가요?"
                }
                next_msg = questions_by_round.get(
                    model.current_round,
                    f"마지막으로 이 경험을 되돌아보았을 때 가장 기억에 남는 최종 소회나 팁을 한 말씀 부탁드립니다."
                )
                turns.append(InterviewTurn(
                    round=model.current_round,
                    question=next_msg,
                    original_answer="",
                    extracted_episodes=[],
                    extracted_facts=[],
                    is_drilldown=False
                ))

            model.turns_json = json.dumps([t.model_dump() for t in turns], ensure_ascii=False)
            model.context_notebook_json = notebook.model_dump_json()
            db.commit()

            state = InterviewSessionState(
                session_id=session_uuid,
                topic=model.topic,
                main_keyword=model.main_keyword or "",
                turns=turns,
                context_notebook=notebook,
                status=model.status
            )
            return state, next_msg, is_completed
        finally:
            db.close()

    def generate_outline(self, session_uuid: str) -> ExperienceOutline:
        """Generate structured ExperienceOutline strictly mapped to Context Notebook."""
        db = self._get_db()
        try:
            model = db.query(InterviewSessionModel).filter_by(session_uuid=session_uuid).first()
            if not model:
                raise ValueError(f"세션 '{session_uuid}'를 찾을 수 없습니다.")

            notebook = ContextNotebook.model_validate_json(model.context_notebook_json) if model.context_notebook_json else ContextNotebook()

            kw = model.main_keyword or model.topic
            topic = model.topic

            # Build deterministic 3 SEO Titles combining keyword + real conflict/choice/experience
            titles = [
                f"[{kw}] 직접 겪어보고 정리한 실제 후기와 놓치기 쉬운 시행착오",
                f"내가 다시 {kw} 선택한다면? 실제 비용·시간과 솔직 경험 총정리",
                f"[{kw} 찐후기] 기대와 달랐던 점과 현장에서 체득한 필수 팁"
            ]

            # Build 3~4 H2 sections mapped to episodes
            sections: List[H2SectionOutline] = []
            episodes = notebook.episodes or [
                ContextEpisode(id="E01", situation=topic, problem_or_conflict="선택 고민", action="실행", result="경험")
            ]

            for idx, ep in enumerate(episodes[:4]):
                heading_templates = [
                    f"직접 맞닥뜨린 실제 상황과 고민: {ep.situation[:30]}",
                    f"예상과 완전히 달랐던 순간: {ep.problem_or_conflict}",
                    f"시행착오 끝에 내린 선택과 실제 결과: {ep.action[:30]}",
                    f"현장에서 직접 깨달은 핵심 관찰과 팁: {ep.unique_observation[:30]}"
                ]
                h_name = heading_templates[idx] if idx < len(heading_templates) else f"실제 경험에서 얻은 통찰 #{idx+1}"
                sections.append(H2SectionOutline(
                    heading=h_name,
                    episode_ids=[ep.id],
                    key_facts=ep.specific_numbers or ["실제 현장 체감 데이터"],
                    user_decision=ep.action,
                    expected_vs_actual=f"{ep.problem_or_conflict} -> {ep.result}",
                    photo_placement=f"{ep.id} 상황 직접 촬영 사진 삽입 권장" if notebook.photo_opportunities else None
                ))

            # Ensure at least 3 sections
            while len(sections) < 3:
                idx = len(sections) + 1
                sections.append(H2SectionOutline(
                    heading=f"이런 분께 추천 & 비추천: 솔직한 최종 비교",
                    episode_ids=[],
                    key_facts=notebook.numbers[:2] if notebook.numbers else ["실제 비교 기준"],
                    user_decision="경험 기반 솔직한 평가"
                ))

            intro_dir = (
                f"진부한 '~알아보겠습니다'를 배제하고, {episodes[0].situation[:40]} 당시 "
                f"느꼈던 실제 감정과 고민의 순간에서 출발하십시오."
            )
            concl_dir = (
                f"별도 결론 H2 없이 마지막 부분에서 2~3문장으로 '다시 선택한다면 바꿀 점'과 "
                f"'누구에게 가장 적합한지'를 진솔하게 정리하십시오."
            )

            outline = ExperienceOutline(
                titles=titles[:3],
                intro_direction=intro_dir,
                sections=sections[:4],
                conclusion_direction=concl_dir,
                photo_suggestions=notebook.photo_opportunities or ["직접 촬영한 현장 사진이 있다면 권장 위치에 배치"]
            )

            model.outline_json = outline.model_dump_json()
            model.status = "OUTLINED"
            db.commit()

            logger.info("Experience outline generated for session '%s'", session_uuid)
            return outline
        finally:
            db.close()

    def generate_draft(
        self,
        session_uuid: str,
        outline: Optional[ExperienceOutline] = None
    ) -> Tuple[ExperienceDraft, ExperienceGroundingReport]:
        """Generate complete HTML draft grounded strictly in Context Notebook and verify."""
        db = self._get_db()
        try:
            model = db.query(InterviewSessionModel).filter_by(session_uuid=session_uuid).first()
            if not model:
                raise ValueError(f"세션 '{session_uuid}'를 찾을 수 없습니다.")

            notebook = ContextNotebook.model_validate_json(model.context_notebook_json) if model.context_notebook_json else ContextNotebook()

            if not outline:
                if model.outline_json:
                    outline = ExperienceOutline.model_validate_json(model.outline_json)
                else:
                    outline = self.generate_outline(session_uuid)

            title = outline.titles[0]
            seo_title = f"{model.main_keyword or model.topic} 실제 경험 후기 및 비용 시행착오 총정리"
            meta_desc = f"{model.topic} 직접 겪어보고 작성한 100% 리얼 후기. {len(notebook.episodes)}가지 핵심 에피소드와 실제 시행착오, 추천 팁 완벽 정리."
            slug = generate_slug(f"exp-{model.main_keyword or 'story'}-{session_uuid[:6]}")

            # Build HTML sections from outline & notebook episodes
            sections_html = ""
            for s in outline.sections:
                matched_eps = [ep for ep in notebook.episodes if ep.id in s.episode_ids]
                ep_text_p = ""
                for ep in matched_eps:
                    nums_str = f" (실제 데이터: {', '.join(ep.specific_numbers)})" if ep.specific_numbers else ""
                    ep_text_p += f"""
                    <div style='background:#f8fafc; border-left:4px solid #3b82f6; padding:16px 20px; margin:16px 0; border-radius:0 8px 8px 0;'>
                      <p style='margin:0 0 8px 0; color:#1e293b; font-size:16px; line-height:1.8;'>{ep.action}{nums_str}</p>
                      <p style='margin:0; font-size:14px; color:#64748b;'><strong>당시의 생각:</strong> {ep.emotion} &middot; <strong>결과:</strong> {ep.result}</p>
                    </div>
                    """
                if not ep_text_p:
                    ep_text_p = f"<p style='color:#334155; line-height:1.8; font-size:16px;'>{s.user_decision}</p>"

                photo_html = f"<div style='background:#eff6ff; border:1px dashed #60a5fa; border-radius:8px; padding:12px; text-align:center; color:#1d4ed8; font-size:13px; margin:14px 0;'>📷 [사진 추천 배치] {s.photo_placement}</div>" if s.photo_placement else ""

                sections_html += f"""
                <section style='margin-bottom:32px;'>
                  <h2 style='font-size:20px; font-weight:800; color:#0f172a; border-bottom:2px solid #e2e8f0; padding-bottom:8px; margin:28px 0 16px 0;'>{s.heading}</h2>
                  {ep_text_p}
                  {photo_html}
                </section>
                """

            # Introduction without cliches
            first_ep = notebook.episodes[0] if notebook.episodes else None
            intro_text = f"실제로 {first_ep.situation if first_ep else model.topic} 당시를 돌이켜보면, 처음부터 순탄했던 것만은 아니었습니다. 직접 겪어보고 나서야 비로소 알게 된 진짜 현실과 시행착오를 가감 없이 공유하고자 합니다."

            # Conclusion without separate H2
            conclusion_text = f"만약 제가 다시 같은 선택을 해야 한다면 주저 없이 이 경험을 밑거름 삼아 더 나은 준비를 할 것입니다. {model.topic}을(를) 고민 중이신 분들께 저의 실제 시행착오가 실질적인 도움이 되기를 바랍니다."

            # Schema.org BlogPosting
            schema_json = json.dumps({
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": title,
                "description": meta_desc,
                "author": {
                    "@type": "Person",
                    "name": "Experience Contributor"
                }
            }, ensure_ascii=False)

            html_body = f"""
            <div class="experience-article-container" style="max-width:800px; margin:0 auto; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color:#1e293b; line-height:1.8;">
              <script type="application/ld+json">
              {schema_json}
              </script>

              <!-- Hero Card -->
              <div style="background:linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color:#ffffff; border-radius:14px; padding:26px; margin-bottom:30px;">
                <span style="background:#2563eb; color:#ffffff; font-size:12px; font-weight:700; padding:4px 10px; border-radius:14px; display:inline-block; margin-bottom:10px;">실제 경험 인터뷰 기반</span>
                <div style="font-size:24px; font-weight:800; margin:0 0 12px 0; line-height:1.35;">{title}</div>
                <p style="color:#cbd5e1; font-size:15px; margin:0; line-height:1.6;">{meta_desc}</p>
              </div>

              <!-- Introduction -->
              <div style="font-size:17px; color:#334155; line-height:1.85; margin-bottom:28px;">
                <p>{intro_text}</p>
              </div>

              <!-- Main Sections -->
              {sections_html}

              <!-- Integrated Conclusion -->
              <div style="background:#f1f5f9; border-radius:10px; padding:20px 24px; margin-top:28px; border-left:4px solid #2563eb;">
                <p style="margin:0; font-size:15px; color:#334155; line-height:1.75;">{conclusion_text}</p>
              </div>
            </div>
            """

            tags = [model.main_keyword or model.topic, "실제경험", "솔직후기", "시행착오"]

            draft = ExperienceDraft(
                title=title,
                seo_title=seo_title,
                meta_description=meta_desc,
                slug=slug,
                html_content=html_body,
                excerpt=meta_desc,
                tags=tags,
                episodes_used=[ep.id for ep in notebook.episodes],
                generator_version="1.0",
                quality_profile="experience",
                prompt_version="v3.0-experience-engine"
            )

            # Experience Grounding Check
            grounding_report = ExperienceGroundingService.verify_draft(draft, notebook)

            model.draft_json = draft.model_dump_json()
            model.grounding_report_json = grounding_report.model_dump_json()
            model.status = "DRAFTED"
            db.commit()

            logger.info("Experience draft generated and grounded for session '%s' (Status: %s)", session_uuid, grounding_report.status)
            return draft, grounding_report
        finally:
            db.close()

    def approve_and_create_post(
        self,
        session_uuid: str,
        db: Session,
        site_id: Optional[int] = None
    ) -> Post:
        """Approve grounded Experience draft and create database Post record."""
        model = db.query(InterviewSessionModel).filter_by(session_uuid=session_uuid).first()
        if not model or not model.draft_json:
            raise ValueError(f"세션 '{session_uuid}'의 완성된 초안을 찾을 수 없습니다.")

        draft = ExperienceDraft.model_validate_json(model.draft_json)
        grounding_report = ExperienceGroundingReport.model_validate_json(model.grounding_report_json) if model.grounding_report_json else None

        grounding_status = grounding_report.status if grounding_report else "PASS"
        post_status = PostStatusEnum.APPROVED.value if grounding_status == "PASS" else PostStatusEnum.REVIEW.value

        post = Post(
            title=draft.title,
            slug=draft.slug,
            rendered_content=draft.html_content,
            excerpt=draft.excerpt,
            seo_title=draft.seo_title,
            meta_description=draft.meta_description,
            vertical="EXPERIENCE",
            site_id=site_id,
            status=post_status,
            quality_status=QualityStatusEnum.PASS.value if grounding_status == "PASS" else QualityStatusEnum.REVIEW.value,
            experience_grounding_status=grounding_status,
            generator_version=draft.generator_version,
            quality_profile=draft.quality_profile,
            prompt_version=draft.prompt_version,
            article_json=draft.model_dump_json(),
            failure_reason=None if grounding_status == "PASS" else f"경험 그라운딩 검토 필요: {grounding_report.summary if grounding_report else ''}"
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        model.post_id = post.id
        model.status = "APPROVED"
        db.commit()

        logger.info("Experience draft approved into Post ID #%d (Status: %s)", post.id, post.status)
        return post
