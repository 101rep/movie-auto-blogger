# -*- coding: utf-8 -*-
import base64
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
import requests
from requests.auth import HTTPBasicAuth
from sqlalchemy.orm import Session

from config import settings
from database.models import Content, Comment
from integrations.factory import get_ai_provider
from integrations.providers.real_ai_provider import RealAIProvider

logger = logging.getLogger("WordPressService")

class WordPressService:
    """
    WordPress REST API Publisher and Content Bridge Service
    Connects Threads Social Commerce with WordPress (trendspot24.com)
    Powered by Universal Blog Quality Engine (E-E-A-T, Anti-Cliche, People-First)
    """

    def __init__(self, site_url: Optional[str] = None, username: Optional[str] = None, app_password: Optional[str] = None):
        self.site_url = (site_url or getattr(settings, "WORDPRESS_URL", "https://item.travelpick24.com")).rstrip("/")
        self.username = username or getattr(settings, "WORDPRESS_USERNAME", "")
        raw_pw = app_password or getattr(settings, "WORDPRESS_APPLICATION_PASSWORD", "")
        self.app_password = raw_pw.replace(" ", "")
        self.api_base_url = f"{self.site_url}/wp-json/wp/v2"

    def _get_auth(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.username, self.app_password)

    def test_connection(self) -> Dict[str, Any]:
        """Verify connection and credentials to WordPress REST API"""
        if not self.site_url or not self.username or not self.app_password:
            return {
                "status": "ERROR",
                "connected": False,
                "message": "워드프레스 설정(WORDPRESS_URL, USERNAME, APP_PASSWORD)이 누락되었습니다."
            }

        url = f"{self.api_base_url}/users/me"
        try:
            resp = requests.get(url, auth=self._get_auth(), timeout=10)
            if resp.status_code == 200:
                user_info = resp.json()
                return {
                    "status": "SUCCESS",
                    "connected": True,
                    "site_url": self.site_url,
                    "user_name": user_info.get("name", self.username),
                    "user_id": user_info.get("id"),
                    "message": f"워드프레스 연결 성공! (사이트: {self.site_url}, 계정: {user_info.get('name')})"
                }
            elif resp.status_code in (401, 403):
                return {
                    "status": "AUTH_ERROR",
                    "connected": False,
                    "message": "워드프레스 인증 실패: 아이디 또는 애플리케이션 비밀번호를 확인해주세요."
                }
            else:
                return {
                    "status": "HTTP_ERROR",
                    "connected": False,
                    "code": resp.status_code,
                    "message": f"워드프레스 응답 오류 (HTTP {resp.status_code})"
                }
        except Exception as e:
            return {
                "status": "CONNECT_ERROR",
                "connected": False,
                "message": f"워드프레스 연결 실패: {str(e)}"
            }

    def get_or_create_category(self, cat_name: str) -> Optional[int]:
        clean_name = cat_name.strip()
        if not clean_name:
            return None
        url = f"{self.api_base_url}/categories"
        try:
            resp = requests.get(url, auth=self._get_auth(), params={"search": clean_name}, timeout=10)
            if resp.status_code == 200:
                cats = resp.json()
                for c in cats:
                    if c.get("name", "").lower() == clean_name.lower():
                        return c["id"]
            create_resp = requests.post(url, auth=self._get_auth(), json={"name": clean_name}, timeout=10)
            if create_resp.status_code in (200, 201):
                return create_resp.json().get("id")
        except Exception as e:
            logger.warning(f"Category lookup/create error: {e}")
        return None

    def publish_article(
        self,
        title: str,
        content_html: str,
        excerpt: str = "",
        categories: Optional[List[str]] = None,
        status: str = "publish"
    ) -> Dict[str, Any]:
        """Publish a post to WordPress REST API"""
        url = f"{self.api_base_url}/posts"
        cat_ids = []
        if categories:
            for cat in categories:
                cid = self.get_or_create_category(cat)
                if cid:
                    cat_ids.append(cid)

        payload = {
            "title": title,
            "content": content_html,
            "status": status,
            "excerpt": excerpt
        }
        if cat_ids:
            payload["categories"] = cat_ids

        try:
            resp = requests.post(url, auth=self._get_auth(), json=payload, timeout=20)
            if resp.status_code in (200, 201):
                data = resp.json()
                post_id = data.get("id")
                permalink = data.get("link", f"{self.site_url}/?p={post_id}")
                if "cloudwaysapps.com" in permalink:
                    permalink = permalink.replace("https://wordpress-1670576-6680151.cloudwaysapps.com", self.site_url)
                logger.info(f"WordPress article published successfully: ID={post_id}, URL={permalink}")
                return {
                    "status": "SUCCESS",
                    "post_id": post_id,
                    "url": permalink,
                    "title": title
                }
            else:
                logger.error(f"WordPress publish failed: {resp.status_code} - {resp.text[:200]}")
                return {
                    "status": "FAILED",
                    "code": resp.status_code,
                    "message": resp.text[:200]
                }
        except Exception as e:
            logger.error(f"WordPress publish exception: {e}")
            return {
                "status": "ERROR",
                "message": str(e)
            }

    def generate_eeat_blog_post(self, content: Content) -> Dict[str, Any]:
        """
        Universal Content Quality and Experience Engine
        Converts Threads content into an in-depth, trustworthy, E-E-A-T rich blog post
        Anti-Cliche: Strips out AI buzzwords and robotic openers
        People-First: First-hand experience notes, honest pros/cons, setup guide
        """
        prod = content.product
        prod_name = prod.name if prod else "큐레이션 아이템"
        prod_price = f"{prod.price:,}원" if prod and prod.price else "가성비 특가"

        ai = get_ai_provider()

        system_instruction = (
            "당신은 10년 차 IT 테크 및 라이프스타일 장비 전문 칼럼니스트이자 프로 블로거입니다.\n"
            "규칙 1 (Anti-Cliche): '혁신적인', '알아보겠습니다', '살펴보겠습니다', '총정리', '어떠셨나요?' 같은 식상한 AI 상투어구를 절대로 쓰지 마세요.\n"
            "규칙 2 (E-E-A-T and People-First): 실제 본인이 매일 책상에서 사용해 본 사람의 생생하고 진솔한 말투로 작성하세요.\n"
            "규칙 3 (구조화): 핵심 요약, 실사용자가 느낀 결정적 장점, 솔직히 아쉬운 점, 이런 분에게 추천 코너로 체계적 HTML 마크업으로 구성하세요."
        )

        blog_brand = "아이템픽24" if "item" in self.site_url else "트렌드스팟24"
        user_prompt = f"""
다음 스레드 콘텐츠를 바탕으로 워드프레스 블로그 '{blog_brand}'에 게시할 고품질 리뷰 포스팅을 작성해 주세요.

[상품명]: {prod_name}
[가격대]: {prod_price}
[스레드 원문]:
{content.body}

[작성 요구사항]:
1. 글 제목: 독자의 시선을 사로잡는 구체적인 제목 (예: 실사용 솔직 리뷰 | ...)
2. 본문 내용 (HTML 형식, <h2>, <h3>, <p>, <ul>, <blockquote> 태그 활용)
   - 상단: 제품을 사게 된 배경과 3줄 핵심 요약 카드
   - 중반: 실제 사용하며 느낀 장점과 구체적인 디테일
   - 후반: 솔직한 단점/아쉬운 점과 구매 가이드
   - 하단: 쿠팡 파트너스 공정위 문구 포함
3. 메타 요약문 (Excerpt): 2문장 내외

출력 형식:
TITLE: [블로그 제목]
EXCERPT: [요약문]
CONTENT:
[HTML 본문]
"""

        if isinstance(ai, RealAIProvider):
            try:
                raw = ai.generate_text(user_prompt, system_prompt=system_instruction)
                title_match = re.search(r"TITLE:\s*(.+)", raw)
                excerpt_match = re.search(r"EXCERPT:\s*(.+)", raw)
                content_match = re.search(r"CONTENT:\s*([\s\S]+)", raw)

                title = title_match.group(1).strip() if title_match else f"{prod_name} 실사용 솔직 리뷰 및 가이드"
                excerpt = excerpt_match.group(1).strip() if excerpt_match else f"{prod_name} 실사용자가 전하는 디테일 리뷰"
                body_html = content_match.group(1).strip() if content_match else raw
                return {"title": title, "excerpt": excerpt, "html": body_html}
            except Exception as e:
                logger.warning(f"AI generation failed for blog post, using fallback: {e}")

        # Fallback high-quality template
        title = f"[내돈내산 솔직후기] {prod_name} 일주일 실사용 장단점 총평"
        excerpt = f"{prod_name} 실제 사용자가 전하는 솔직한 스펙 비교와 장단점 분석 가이드입니다."
        body_html = f"""
<div style="background: #f8fafc; border-left: 4px solid #3b82f6; padding: 16px; margin-bottom: 24px; border-radius: 8px;">
    <h3 style="margin-top: 0; color: #1e3a8a;">💡 실사용자 3줄 핵심 요약</h3>
    <ul style="margin-bottom: 0;">
        <li><strong>체감 만족도:</strong> 기본기가 매우 탄탄하며 마감 품질이 뛰어납니다.</li>
        <li><strong>가장 큰 장점:</strong> 복잡한 세팅 없이 개봉 직후 바로 쾌적하게 쓸 수 있는 직관성.</li>
        <li><strong>가격 경쟁력:</strong> 현재 기준 {prod_price} 수준으로 동급 대비 가성비 만족도 높음.</li>
    </ul>
</div>

<h2>🔍 매일 쓰면서 체감한 결정적 포인트</h2>
<p>{content.body.replace(chr(10), '<br/>')}</p>

<h2>⚖️ 솔직하게 짚어보는 장점과 아쉬운 점</h2>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 20px 0;">
    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 14px; border-radius: 8px;">
        <h4 style="margin-top: 0; color: #166534;">👍 만족스러운 점</h4>
        <ul>
            <li>공간을 덜 차지하는 콤팩트하고 깔끔한 디자인</li>
            <li>실제 작업 시 발열 및 소음 제어 수준 우수</li>
            <li>동봉된 마감재 및 연결 안정성 합격점</li>
        </ul>
    </div>
    <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 14px; border-radius: 8px;">
        <h4 style="margin-top: 0; color: #991b1b;">👎 아쉬운 점</h4>
        <ul>
            <li>초기 포장 뜯을 때 약간의 포장재 냄새</li>
            <li>휴대용 파우치는 별도 구비 추천</li>
        </ul>
    </div>
</div>

<h2>🎯 이런 분들께 특히 권해드립니다</h2>
<p>평소 책상 정리가 어렵거나 가성비와 심미성을 동시에 챙기고 싶은 직장인 및 테크 크리에이터분들께 적극 추천합니다.</p>

<div style="margin-top: 40px; padding: 14px; background: #fafafa; border: 1px dashed #cbd5e1; border-radius: 6px; font-size: 13px; color: #64748b;">
    <p style="margin: 0;">📢 <strong>안내:</strong> 본 포스팅은 실제 사용 경험을 바탕으로 작성되었으며, 제휴 마케팅 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다.</p>
</div>
"""
        return {"title": title, "excerpt": excerpt, "html": body_html}

    def bridge_content(self, db: Session, content_id: int) -> Dict[str, Any]:
        """
        One-Click and Auto Bridge:
        1. Generates E-E-A-T blog post from Threads Content
        2. Publishes to trendspot24.com WordPress
        3. Updates Content model with wordpress_url and wordpress_post_id
        4. Injects the safe blog link into Threads first reply comment
        """
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return {"status": "ERROR", "message": f"Content {content_id} not found"}

        # 1. Generate E-E-A-T article
        article_data = self.generate_eeat_blog_post(content)

        # 2. Publish to WordPress
        pub_result = self.publish_article(
            title=article_data["title"],
            content_html=article_data["html"],
            excerpt=article_data["excerpt"],
            categories=["IT/테크", "라이프스타일"]
        )

        if pub_result.get("status") == "SUCCESS":
            post_id = pub_result["post_id"]
            post_url = pub_result["url"]

            content.wordpress_post_id = post_id
            content.wordpress_url = post_url
            content.wordpress_status = "PUBLISHED"

            # 3. Update or prepend Threads comment with bridge link
            bridge_text = f"📌 제품 상세 스펙 비교 & 실사용 꿀팁 총정리:\n👉 {post_url}\n\n(쿠팡 파트너스 활동의 일환으로 수수료를 제공받을 수 있습니다)"
            
            existing_comment = db.query(Comment).filter(Comment.content_id == content_id).first()
            if existing_comment:
                existing_comment.body = f"{bridge_text}\n\n{existing_comment.body}"
            else:
                new_c = Comment(content_id=content_id, body=bridge_text, comment_order=1)
                db.add(new_c)

            db.commit()
            db.refresh(content)

            return {
                "status": "SUCCESS",
                "content_id": content.id,
                "wordpress_post_id": post_id,
                "wordpress_url": post_url,
                "title": article_data["title"],
                "message": "워드프레스(trendspot24.com) 발행 및 스레드 첫 댓글 연동 완료!"
            }
        else:
            content.wordpress_status = "FAILED"
            db.commit()
            return pub_result