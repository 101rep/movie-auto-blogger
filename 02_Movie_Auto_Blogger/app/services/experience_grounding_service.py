"""Experience Grounding Service verifying experiential claims against Context Notebook.

Enforces:
- 1st person experiential claims in drafts must be grounded in Context Notebook.
- Hallucinated or ungrounded personal claims result in REVIEW / FAIL status.
- Prevents auto-publishing of ungrounded experience articles.
"""
import re
from typing import Any, Dict, List, Optional
from app.ai.experience_schemas import ContextNotebook, ExperienceDraft, ExperienceGroundingReport, GroundingClaim
from app.utils.logging import get_logger

logger = get_logger("experience_grounding_service")


class ExperienceGroundingService:
    """Verifies that personal experience claims in an article draft originate from the Context Notebook."""

    @classmethod
    def verify_draft(
        cls,
        draft: ExperienceDraft,
        notebook: ContextNotebook
    ) -> ExperienceGroundingReport:
        """Audit experiential assertions in draft against Context Notebook episodes and facts."""
        claims: List[GroundingClaim] = []

        # Extract text sentences from HTML content
        clean_text = re.sub(r'<[^>]+>', ' ', draft.html_content)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        sentences = [s.strip() for s in re.split(r'[.?!]\s+', clean_text) if len(s.strip()) > 10]

        # Gather notebook grounding corpus
        notebook_corpus = []
        episode_map = {}
        for ep in notebook.episodes:
            ep_text = f"{ep.situation} {ep.problem_or_conflict} {ep.action} {ep.result} {ep.emotion} {' '.join(ep.specific_numbers)} {ep.unique_observation}".lower()
            notebook_corpus.append(ep_text)
            episode_map[ep.id] = ep_text

        all_facts = " ".join(notebook.facts + notebook.numbers + notebook.comparisons + notebook.mistakes + notebook.discoveries).lower()

        # Identify personal experience claim markers
        experience_markers = [
            "저는", "제가", "직접", "실제로", "경험해보니", "방문했을 때",
            "써보니", "먹어보니", "가보니", "겪었던", "체감상", "기억에 남는",
            "걸렸습니다", "들었습니다", "느꼈습니다", "결정했습니다"
        ]

        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if sentence makes a personal experience claim
            is_claim = any(m in sentence_lower for m in experience_markers)

            if is_claim:
                # Check if grounded in any episode or fact
                matched_ep_id = None
                is_grounded = False

                for ep_id, ep_text in episode_map.items():
                    # Check keyword overlap between claim sentence and episode text
                    claim_words = set(re.findall(r'[가-힣a-zA-Z0-9]{2,}', sentence_lower))
                    ep_words = set(re.findall(r'[가-힣a-zA-Z0-9]{2,}', ep_text))
                    overlap = claim_words & ep_words
                    if len(overlap) >= 2 or any(num in ep_text for num in re.findall(r'\d+', sentence)):
                        is_grounded = True
                        matched_ep_id = ep_id
                        break

                if not is_grounded and len(set(re.findall(r'[가-힣a-zA-Z0-9]{2,}', sentence_lower)) & set(re.findall(r'[가-힣a-zA-Z0-9]{2,}', all_facts))) >= 2:
                    is_grounded = True

                claims.append(GroundingClaim(
                    claim_text=sentence,
                    is_grounded=is_grounded,
                    matched_episode_id=matched_ep_id,
                    source_type="user_interview" if is_grounded else "unverified_claim",
                    detail="Context Notebook 근거 확인됨" if is_grounded else "Context Notebook에 없는 1인칭 경험 진술 (근거 불충분)"
                ))

        total_claims = len(claims)
        grounded_count = sum(1 for c in claims if c.is_grounded)
        ungrounded_count = sum(1 for c in claims if not c.is_grounded)
        ungrounded_claims = [c for c in claims if not c.is_grounded]
        grounding_ratio = (grounded_count / total_claims) if total_claims > 0 else 1.0

        if ungrounded_count == 0:
            status = "PASS"
            is_passed = True
            summary = f"모든 경험적 진술({grounded_count}건)이 Context Notebook에 정상 근거함."
        elif ungrounded_count <= 1 and total_claims >= 4:
            status = "REVIEW"
            is_passed = False
            summary = f"근거 미확인 경험 진술 {ungrounded_count}건 감지 (검토 필요)."
        else:
            status = "FAIL"
            is_passed = False
            summary = f"근거 미확인 경험 진술 {ungrounded_count}건 발견 (할루시네이션 위험)."

        report = ExperienceGroundingReport(
            total_claims=total_claims,
            grounded_count=grounded_count,
            ungrounded_count=ungrounded_count,
            grounded_claims_count=grounded_count,
            grounding_ratio=grounding_ratio,
            is_passed=is_passed,
            status=status,
            claims=claims,
            ungrounded_claims=ungrounded_claims,
            summary=summary
        )

        logger.info("Experience grounding report: Status=%s (Grounded: %d/%d)", status, grounded_count, total_claims)
        return report
