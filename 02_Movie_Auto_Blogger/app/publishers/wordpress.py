"""WordPress REST API publisher implementation."""
import base64
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx

from app.config import get_settings
from app.publishers.base import BasePublisher, PostStatus, PublishRequest, PublishResult
from app.utils.logging import get_logger

logger = get_logger("wordpress_publisher")


class WordPressPublisher(BasePublisher):
    """Client for WordPress REST API supporting posts, media, taxonomies, and future scheduling."""

    def __init__(
        self,
        site_url: Optional[str] = None,
        username: Optional[str] = None,
        app_password: Optional[str] = None
    ) -> None:
        settings = get_settings()
        self.site_url = (site_url if site_url is not None else (settings.WORDPRESS_URL or "")).rstrip("/")
        self.username = username if username is not None else (settings.WORDPRESS_USERNAME or "")
        # Remove whitespace in application password if present
        raw_pw = app_password if app_password is not None else (settings.WORDPRESS_APPLICATION_PASSWORD or "")
        self.app_password = raw_pw.replace(" ", "")

        self._category_cache: Dict[str, int] = {}
        self._tag_cache: Dict[str, int] = {}

    @property
    def api_base_url(self) -> str:
        return f"{self.site_url}/wp-json/wp/v2"

    def _get_headers(self) -> Dict[str, str]:
        """Generate HTTP Basic Auth header for WordPress Application Password."""
        credentials = f"{self.username}:{self.app_password}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return {
            "Authorization": f"Basic {encoded}",
            "Accept": "application/json"
        }

    async def health_check(self) -> Dict[str, Any]:
        """Test WordPress REST API connectivity, authentication, and permissions."""
        if not self.site_url or not self.username or not self.app_password:
            return {
                "success": False,
                "message": "워드프레스 설정이 누락되었습니다 (WORDPRESS_URL, USERNAME, APPLICATION_PASSWORD 확인 필요)"
            }

        url = f"{self.api_base_url}/users/me"
        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                res = await client.get(url, headers=self._get_headers())
                if res.status_code == 200:
                    user_data = res.json()
                    name = user_data.get("name", self.username)
                    return {
                        "success": True,
                        "message": f"워드프레스 연결 성공! (인증 사용자: {name})"
                    }
                elif res.status_code in (401, 403):
                    return {
                        "success": False,
                        "message": "워드프레스 인증 실패: 사용자 아이디 또는 애플리케이션 비밀번호(Application Password)를 확인하세요."
                    }
                elif res.status_code == 404:
                    return {
                        "success": False,
                        "message": f"워드프레스 REST API 엔드포인트를 찾을 수 없습니다 ({url}). 사이트 URL 또는 고유주소(Permalink) 설정을 확인하세요."
                    }
                else:
                    return {
                        "success": False,
                        "message": f"워드프레스 서버 응답 오류 (HTTP 상태 코드: {res.status_code})"
                    }
        except httpx.ConnectError:
            return {"success": False, "message": f"워드프레스 사이트에 연결할 수 없습니다: {self.site_url}"}
        except httpx.TimeoutException:
            return {"success": False, "message": "워드프레스 서버 응답 시간 초과"}
        except Exception as e:
            logger.error("WordPress health check error: %s", str(e), exc_info=True)
            return {"success": False, "message": f"워드프레스 연결 오류: {str(e)}"}

    async def get_or_create_category(self, name: str) -> Optional[int]:
        """Search for existing category by name or create a new one."""
        clean_name = name.strip()
        if not clean_name:
            return None

        if clean_name in self._category_cache:
            return self._category_cache[clean_name]

        url = f"{self.api_base_url}/categories"
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                # 1. Search existing
                res = await client.get(url, headers=headers, params={"search": clean_name})
                if res.status_code == 200:
                    categories = res.json()
                    for cat in categories:
                        if cat.get("name", "").lower() == clean_name.lower():
                            cat_id = cat.get("id")
                            self._category_cache[clean_name] = cat_id
                            return cat_id

                # 2. Create if missing
                create_res = await client.post(url, headers=headers, json={"name": clean_name})
                if create_res.status_code in (200, 201):
                    new_cat = create_res.json()
                    cat_id = new_cat.get("id")
                    self._category_cache[clean_name] = cat_id
                    return cat_id
                elif create_res.status_code == 400:
                    # Term might already exist with slightly different search query
                    err_data = create_res.json()
                    term_id = err_data.get("data", {}).get("term_id")
                    if term_id:
                        self._category_cache[clean_name] = term_id
                        return term_id
        except Exception as e:
            logger.warning("Failed to resolve category '%s': %s", clean_name, str(e))

        return None

    async def get_or_create_tag(self, name: str) -> Optional[int]:
        """Search for existing tag by name or create a new one."""
        clean_name = name.strip().lstrip("#")
        if not clean_name:
            return None

        if clean_name in self._tag_cache:
            return self._tag_cache[clean_name]

        url = f"{self.api_base_url}/tags"
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                # 1. Search existing
                res = await client.get(url, headers=headers, params={"search": clean_name})
                if res.status_code == 200:
                    tags = res.json()
                    for tag in tags:
                        if tag.get("name", "").lower() == clean_name.lower():
                            tag_id = tag.get("id")
                            self._tag_cache[clean_name] = tag_id
                            return tag_id

                # 2. Create if missing
                create_res = await client.post(url, headers=headers, json={"name": clean_name})
                if create_res.status_code in (200, 201):
                    new_tag = create_res.json()
                    tag_id = new_tag.get("id")
                    self._tag_cache[clean_name] = tag_id
                    return tag_id
                elif create_res.status_code == 400:
                    err_data = create_res.json()
                    term_id = err_data.get("data", {}).get("term_id")
                    if term_id:
                        self._tag_cache[clean_name] = term_id
                        return term_id
        except Exception as e:
            logger.warning("Failed to resolve tag '%s': %s", clean_name, str(e))

        return None

    async def upload_media(
        self,
        file_bytes: bytes,
        filename: str,
        alt_text: str,
        content_type: str = "image/jpeg"
    ) -> Optional[int]:
        """Upload media file to WordPress and update alt text."""
        url = f"{self.api_base_url}/media"
        headers = self._get_headers()
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        headers["Content-Type"] = content_type

        try:
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                res = await client.post(url, headers=headers, content=file_bytes)
                if res.status_code in (200, 201):
                    data = res.json()
                    media_id = data.get("id")
                    logger.info("Uploaded WordPress media successfully (ID: %s)", media_id)

                    # Update alt text
                    if media_id and alt_text:
                        await client.post(
                            f"{self.api_base_url}/media/{media_id}",
                            headers=self._get_headers(),
                            json={"alt_text": alt_text}
                        )
                    return media_id
                else:
                    logger.error("WordPress media upload failed with status %d: %s", res.status_code, res.text)
                    return None
        except Exception as e:
            logger.error("Media upload exception: %s", str(e), exc_info=True)
            return None

    async def publish_post(self, request: PublishRequest) -> PublishResult:
        """Create or update post with idempotency protection against duplicate posts."""
        headers = self._get_headers()

        # 1. Resolve categories and tags
        category_ids: List[int] = []
        for cat_name in request.categories:
            cid = await self.get_or_create_category(cat_name)
            if cid:
                category_ids.append(cid)

        tag_ids: List[int] = []
        for tag_name in request.tags[:8]:  # Limit to 8 tags max per Section 27
            tid = await self.get_or_create_tag(tag_name)
            if tid:
                tag_ids.append(tid)

        # 2. Build payload
        payload: Dict[str, Any] = {
            "title": request.title,
            "content": request.content,
            "status": request.status.value,
        }
        if request.excerpt:
            payload["excerpt"] = request.excerpt
        if request.slug:
            payload["slug"] = request.slug
        if request.featured_media_id:
            payload["featured_media"] = request.featured_media_id
        if category_ids:
            payload["categories"] = category_ids
        if tag_ids:
            payload["tags"] = tag_ids

        # Future publication schedule (UTC GMT date format and local date format)
        if request.status == PostStatus.FUTURE:
            if request.scheduled_at:
                payload["date_gmt"] = request.scheduled_at
            if request.scheduled_at_local:
                payload["date"] = request.scheduled_at_local

        # 3. Idempotency Check: Verify if a post with this slug OR title already exists on WordPress
        existing_post_id: Optional[int] = None
        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                # 3-1. Check by slug
                if request.slug:
                    slug_check = await client.get(
                        f"{self.api_base_url}/posts",
                        headers=headers,
                        params={"slug": request.slug, "status": "any"}
                    )
                    if slug_check.status_code == 200:
                        posts = slug_check.json()
                        if posts and len(posts) > 0:
                            existing_post_id = posts[0].get("id")
                            logger.info("Found existing WordPress post for slug '%s' (ID: %d). Updating instead of duplicating.", request.slug, existing_post_id)

                # 3-2. Check by title if not found by slug
                if not existing_post_id and request.title:
                    import html, re
                    clean_req_title = html.unescape(request.title).strip()
                    core_words = [w for w in re.sub(r"[^\w\s가-힣0-9a-zA-Z]", " ", clean_req_title).split() if len(w) >= 2 and w not in ["영화", "줄거리", "개봉일", "출연진", "등장인물", "정보", "총정리", "및", "포인트", "가이드", "솔직", "후기", "리뷰"]]
                    search_query = core_words[0] if core_words else clean_req_title[:20]

                    title_check = await client.get(
                        f"{self.api_base_url}/posts",
                        headers=headers,
                        params={"search": search_query, "status": "publish,future,draft", "per_page": 10}
                    )
                    if title_check.status_code == 200:
                        candidates = title_check.json()
                        for c in candidates:
                            c_title = html.unescape(c.get("title", {}).get("rendered", "")).strip()
                            norm_req = "".join(clean_req_title.split()).lower()
                            norm_c = "".join(c_title.split()).lower()
                            if norm_req == norm_c:
                                existing_post_id = c.get("id")
                                logger.warning(
                                    "Detected duplicate WordPress post by exact title '%s' matches existing ID %d ('%s'). Updating existing post to prevent duplicate publication!",
                                    clean_req_title, existing_post_id, c_title
                                )
                                break
        except Exception as e:
            logger.warning("WordPress remote idempotency/deduplication check failed: %s", str(e))

        # 4. Create or Update Post
        try:
            async with httpx.AsyncClient(timeout=25.0, verify=False) as client:
                if existing_post_id:
                    post_url = f"{self.api_base_url}/posts/{existing_post_id}"
                else:
                    post_url = f"{self.api_base_url}/posts"

                # [1차 검증] WordPress POST 요청
                res = await client.post(post_url, headers=headers, json=payload)
                if res.status_code not in (200, 201):
                    err_msg = f"1차 POST 요청 실패 (HTTP {res.status_code}): {res.text[:200]}"
                    logger.error(err_msg)
                    return PublishResult(success=False, error_message=err_msg)

                resp_data = res.json()
                post_id = resp_data.get("id")

                # [2차 검증] post_id 확인
                if not post_id or not isinstance(post_id, int) or post_id <= 0:
                    err_msg = f"2차 검증 실패: WordPress post_id 없음 또는 유효하지 않음 (응답: {resp_data})"
                    logger.error(err_msg)
                    return PublishResult(success=False, error_message=err_msg)

                # [3차 검증] GET API 재조회
                get_url = f"{self.api_base_url}/posts/{post_id}"
                get_res = await client.get(get_url, headers=headers)
                if get_res.status_code != 200:
                    err_msg = f"3차 GET 재조회 실패 (HTTP {get_res.status_code}, post_id: {post_id}): {get_res.text[:200]}"
                    logger.error(err_msg)
                    return PublishResult(success=False, remote_post_id=post_id, error_message=err_msg)

                # [4차 검증] status 확인
                get_data = get_res.json()
                if isinstance(get_data, list):
                    get_data = get_data[0] if get_data else resp_data
                if not isinstance(get_data, dict):
                    get_data = resp_data

                verified_status = get_data.get("status") or resp_data.get("status")
                verified_link = get_data.get("link") or resp_data.get("link")
                verified_date = get_data.get("date") or resp_data.get("date") or request.scheduled_at_local or request.scheduled_at

                if not verified_status:
                    err_msg = f"4차 검증 실패: GET 조회 결과 status 필드 부재 (post_id: {post_id})"
                    logger.error(err_msg)
                    return PublishResult(success=False, remote_post_id=post_id, error_message=err_msg)

                # [5차 검증] 실제 예약(future/scheduled) 또는 발행(publish) 확인
                if request.status == PostStatus.FUTURE:
                    if verified_status not in ("future", "scheduled"):
                        err_msg = f"5차 검증 실패: 예약 상태 불일치 (기대: future/scheduled, 실제: {verified_status}, post_id: {post_id})"
                        logger.error(err_msg)
                        return PublishResult(success=False, remote_post_id=post_id, remote_status=verified_status, error_message=err_msg)
                    if not verified_date:
                        err_msg = f"5차 검증 실패: 예약 일시 확인 불가 (post_id: {post_id})"
                        logger.error(err_msg)
                        return PublishResult(success=False, remote_post_id=post_id, remote_status=verified_status, error_message=err_msg)
                elif request.status == PostStatus.PUBLISH:
                    if verified_status != "publish":
                        err_msg = f"5차 검증 실패: 발행 상태 불일치 (기대: publish, 실제: {verified_status}, post_id: {post_id})"
                        logger.error(err_msg)
                        return PublishResult(success=False, remote_post_id=post_id, remote_status=verified_status, error_message=err_msg)

                logger.info(
                    "WordPress 5단계 검증 통과 성공! [%s] (ID: %s, Status: %s, URL: %s)",
                    "updated" if existing_post_id else "created",
                    post_id,
                    verified_status,
                    verified_link
                )
                return PublishResult(
                    success=True,
                    remote_post_id=post_id,
                    remote_url=verified_link,
                    remote_status=verified_status
                )
        except Exception as e:
            logger.error("WordPress publish_post exception: %s", str(e), exc_info=True)
            return PublishResult(success=False, error_message=str(e))
