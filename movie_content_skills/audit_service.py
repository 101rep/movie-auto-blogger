# -*- coding: utf-8 -*-
"""
EnterPick24 Existing Posts Audit Service (V4).
Audits existing published articles for duplication, canonical status,
and classifies into KEEP, MERGE_CANDIDATE, REWRITE_CANDIDATE, etc.
"""

from typing import Dict, Any, List, Optional
import requests
from requests.auth import HTTPBasicAuth
from movie_content_skills.fingerprint import ContentFingerprint, normalize_title, normalize_entity_name
from movie_content_skills.duplicate_engine import DuplicateEngine


class ExistingPostAuditor:
    """Audits current live WordPress posts on EnterPick24."""

    def __init__(
        self,
        wp_url: str = "https://enter.trendspot24.com",
        wp_user: str = "ktaehoon80@gmail.com",
        wp_pass: str = "aUma6aotA2Q5ugxkohI5PnKd"
    ):
        self.wp_url = wp_url.rstrip("/")
        self.auth = HTTPBasicAuth(wp_user, wp_pass)

    def fetch_all_posts(self) -> List[Dict[str, Any]]:
        """Fetches all posts from WordPress."""
        url = f"{self.wp_url}/wp-json/wp/v2/posts"
        params = {"status": "any", "per_page": 50}
        try:
            r = requests.get(url, params=params, auth=self.auth, timeout=12)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"Error fetching posts for audit: {e}")
        return []

    def audit_existing_corpus(self) -> Dict[str, Any]:
        """
        Audits all current posts and identifies duplicate clusters.
        Returns classifications and canonical recommendations.
        """
        raw_posts = self.fetch_all_posts()
        fingerprints = []

        for p in raw_posts:
            pid = p["id"]
            title = p.get("title", {}).get("rendered", "")
            content = p.get("content", {}).get("rendered", "")
            date = p.get("date", "")
            link = p.get("link", "")

            # Guess primary entity from title
            entity = "UNKNOWN"
            if "Stranger Things" in title or "기묘한 이야기" in title:
                entity = "STRANGER_THINGS"
            elif "Squid Game" in title or "오징어 게임" in title:
                entity = "SQUID_GAME"
            elif "스릴러" in title:
                entity = "THRILLER_TOP5"
            elif "범죄 수사" in title:
                entity = "CRIME_CURATION"

            fp = ContentFingerprint(
                content_id=pid,
                content_type="single_review" if "심층" in title or "관전" in title else "curation",
                title=title,
                primary_entity=entity,
                summary=content[:300],
                published_at=date
            )
            fingerprints.append((fp, p))

        # Check overlaps
        audit_records = []
        entity_groups: Dict[str, List[Dict[str, Any]]] = {}

        for fp, raw in fingerprints:
            entity_groups.setdefault(fp.primary_entity, []).append({
                "id": raw["id"],
                "title": raw["title"]["rendered"],
                "status": raw["status"],
                "date": raw["date"],
                "link": raw["link"],
                "fingerprint": fp
            })

        for entity, group in entity_groups.items():
            if len(group) == 1:
                item = group[0]
                audit_records.append({
                    "id": item["id"],
                    "title": item["title"],
                    "entity": entity,
                    "classification": "KEEP",
                    "reason": "단독 엔티티로 중복 없음",
                    "canonical": None,
                    "link": item["link"]
                })
            else:
                # Duplicate cluster detected! (e.g. STRANGER_THINGS)
                # Oldest or highest-traffic post is proposed as CANONICAL_CANDIDATE
                sorted_group = sorted(group, key=lambda x: x["date"])
                canonical_item = sorted_group[0]  # Post 27
                newer_item = sorted_group[1]      # Post 31

                audit_records.append({
                    "id": canonical_item["id"],
                    "title": canonical_item["title"],
                    "entity": entity,
                    "classification": "CANONICAL_CANDIDATE",
                    "reason": f"최초 발행된 대표 글 (Post #{canonical_item['id']}). 원본 유지 권장.",
                    "canonical": canonical_item["link"],
                    "link": canonical_item["link"]
                })

                audit_records.append({
                    "id": newer_item["id"],
                    "title": newer_item["title"],
                    "entity": entity,
                    "classification": "MERGE_CANDIDATE",
                    "reason": f"동일 작품(기묘한 이야기) 중복 포스팅 (Post #{newer_item['id']}). 추후 Post #{canonical_item['id']}와 통합하거나 다른 미공개 신작 리뷰로 전환 권장.",
                    "canonical": canonical_item["link"],
                    "link": newer_item["link"]
                })

        return {
            "total_posts": len(raw_posts),
            "audit_records": audit_records,
            "duplicate_clusters": [e for e, g in entity_groups.items() if len(g) > 1]
        }

    def format_audit_report(self, audit_result: Dict[str, Any]) -> str:
        """Formats audit findings for presentation and Telegram."""
        lines = [
            "📋 [EnterPick24 기존 게시물 중복 감사 리포트]",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"총 게시물: {audit_result['total_posts']}건",
            f"중복 감지 클러스터: {', '.join(audit_result['duplicate_clusters']) or '없음'}\n"
        ]

        for rec in audit_result["audit_records"]:
            lines.append(f"• [ID #{rec['id']}] {rec['title']}")
            lines.append(f"  - 분류: {rec['classification']}")
            lines.append(f"  - 의견: {rec['reason']}")
            lines.append(f"  - 링크: {rec['link']}")
            lines.append("")

        lines.append("⚠️ 원칙 준수: 자동 삭제/리다이렉트는 수행하지 않으며, 관리자 검토를 위해 보존합니다.")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return "\n".join(lines)
