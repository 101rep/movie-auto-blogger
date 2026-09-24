"""Universal Single-Site Pipeline Runner for all 8 Content Verticals."""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.registry import get_platform_registry
from app.core.verticals import VerticalType
from app.database.models import Post, PostStatusEnum, QualityStatusEnum, Site, utc_now
from app.publishers.base import PostStatus, PublishRequest
from app.publishers.wordpress import WordPressPublisher
from app.services.quality_service import QualityGateService
from app.utils.logging import get_logger

logger = get_logger("single_site_runner")


class SingleSiteRunner:
    """Executes full automated content creation and direct WordPress publishing for any specific site."""

    @staticmethod
    async def run_site(db: Session, site_id: int, topic: Optional[str] = None) -> Dict[str, Any]:
        """Run complete single-site pipeline: Topic -> AI Write -> Quality -> WordPress Publish."""
        site = db.get(Site, site_id)
        if not site:
            raise ValueError(f"Site ID {site_id} not found")

        logger.info("Executing SingleSiteRunner for site [%d] %s (Vertical: %s)", site.id, site.name, site.vertical)
        registry = get_platform_registry()
        v = site.vertical.upper()

        title = ""
        rendered_content = ""
        excerpt = ""
        seo_title = ""
        meta_description = ""
        tags = []
        external_id = uuid.uuid4().hex[:8]
        article_json = "{}"
        featured_image_url = None
        movie_id = None

        from app.services.duplicate_guard import DuplicateGuardService

        # 1. Pipeline branch by Vertical
        if v == "MOVIE":
            from app.modules.movie.module import MovieModule
            from app.services.candidate_service import CandidateService
            mod = registry.get_module(VerticalType.MOVIE) or MovieModule()
            candidates = await mod.collect_candidates(db, limit=30)
            eligible = DuplicateGuardService.filter_unique_candidates(db, site.id, v, candidates, limit=1)
            selected = eligible[0] if eligible else None
            if not selected:
                raise RuntimeError("영화 후보 중 미발행된 신규 후보가 없습니다.")

            external_id = str(selected.external_id)
            enriched = await mod.enrich_item(db, external_id)
            movie = enriched.get("movie")
            movie_id = movie.id if movie else None

            gen = await mod.generate_content(db, enriched)
            art = gen.get("article")
            if not art:
                raise RuntimeError(f"영화 '{selected.title}' AI 본문 생성 실패: 내용이 비어 있어 품질 보호를 위해 발행을 중단합니다.")

            rendered_content = mod.render_html(gen)
            if not rendered_content or len(rendered_content) < 1500:
                raise RuntimeError(f"영화 '{selected.title}' 렌더링 본문 길이 미달 ({len(rendered_content or '')}자). 품질 보호를 위해 발행을 중단합니다.")

            # Guaranteed poster extraction with fallback
            p_url = gen.get("poster_url") or (getattr(movie, "poster_reference", None) if movie else None) or (getattr(movie, "poster_url", None) if movie else None)
            if not p_url or not isinstance(p_url, str) or not p_url.startswith("http"):
                try:
                    import urllib.parse
                    import httpx
                    import re
                    search_kw = f"{selected.title} 영화 공식 포스터"
                    enc_kw = urllib.parse.quote(search_kw)
                    s_url = f"https://search.daum.net/search?w=img&q={enc_kw}"
                    async with httpx.AsyncClient(timeout=8.0) as s_client:
                        s_res = await s_client.get(s_url, headers={"User-Agent": "Mozilla/5.0"})
                        if s_res.status_code == 200:
                            discovered = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)', s_res.text, re.IGNORECASE)
                            valid_urls = [u for u in discovered if not any(x in u.lower() for x in ["icon", "logo", "banner", "ad", "static", "thumb", "profile"])]
                            if valid_urls:
                                p_url = valid_urls[0]
                                logger.info("Discovered fallback poster for movie '%s': %s", selected.title, p_url)
                except Exception as s_err:
                    logger.warning("Poster fallback search error for '%s': %s", selected.title, s_err)

            featured_image_url = p_url

            # Ensure HTML includes hero poster image
            if p_url and ('mab-hero-poster' not in rendered_content):
                poster_block = f'''
                <div class="mab-hero-poster text-center" style="margin-bottom: 20px;">
                  <a href="{p_url}" target="_blank">
                    <img src="{p_url}" alt="{selected.title} 공식 포스터" style="width: 100%; max-width: 320px; max-height: 460px; object-fit: cover; border-radius: 14px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); display: inline-block;" />
                  </a>
                </div>
                '''
                if 'class="mab-hero-card"' in rendered_content:
                    rendered_content = rendered_content.replace('class="mab-hero-card">', f'class="mab-hero-card">\n{poster_block}')
                else:
                    rendered_content = poster_block + "\n" + rendered_content

            title = art.title if art else f"영화 {selected.title} 줄거리 및 개봉일, 출연진 정보 총정리"
            excerpt = art.excerpt if art else f"영화 '{selected.title}'의 줄거리, 개봉일, 출연진 등장인물 및 핵심 관람 포인트 총정리."
            seo_title = art.seo_title if art else title
            meta_description = art.meta_description if art else excerpt
            tags = art.tags if art else ["영화", "영화리뷰", selected.title]
            article_json = art.model_dump_json() if art else "{}"

        elif v == "TRAVEL":
            from app.modules.travel.module import TravelModule
            mod = registry.get_module(VerticalType.TRAVEL) or TravelModule()
            candidates = await mod.collect_candidates(db, limit=30)
            eligible = DuplicateGuardService.filter_unique_candidates(db, site.id, v, candidates, limit=1)
            selected = eligible[0] if eligible else None
            if not selected:
                raise RuntimeError("여행지 후보 중 미발행된 신규 후보가 없습니다.")

            external_id = str(selected.external_id)
            enriched = await mod.enrich_item(db, external_id)
            gen = await mod.generate_content(db, enriched)
            art = gen.get("travel_article")
            rendered_content = mod.render_html(gen)
            title = art.title if art else selected.title
            excerpt = art.excerpt if art else selected.summary
            seo_title = art.seo_title if art else title
            meta_description = art.meta_description if art else excerpt
            tags = art.tags if art else ["여행", "여행가이드", "여행코스"]
            article_json = art.model_dump_json() if art else "{}"
            featured_image_url = art.hero_image_url if art else None

        elif v == "ENTERTAINMENT":
            from app.modules.entertainment.module import EntertainmentModule
            mod = registry.get_module(VerticalType.ENTERTAINMENT) or EntertainmentModule()
            candidates = await mod.collect_candidates(db, limit=20)
            eligible = DuplicateGuardService.filter_unique_candidates(db, site.id, v, candidates, limit=1)
            selected = eligible[0] if eligible else None
            if not selected:
                raise RuntimeError("연예/엔터 후보 중 미발행된 신규 후보가 없습니다.")

            external_id = str(selected.external_id)
            enriched = await mod.enrich_item(db, external_id)
            gen = await mod.generate_content(db, enriched)
            art = gen.get("entertainment_article")
            rendered_content = mod.render_html(gen)
            title = art.title if art else selected.title
            excerpt = art.excerpt if art else selected.summary
            seo_title = art.seo_title if art else title
            meta_description = art.meta_description if art else excerpt
            tags = art.tags if art else ["연예", "K컬처", "방송"]
            article_json = art.model_dump_json() if art else "{}"
            featured_image_url = getattr(art, "hero_image_url", None) if art else None

        elif v == "WELFARE":
            from app.modules.welfare.module import WelfareModule
            mod = registry.get_module(VerticalType.WELFARE) or WelfareModule()
            candidates = await mod.collect_candidates(db, limit=30, site_id=site.id)
            if not candidates:
                candidates = await mod.collect_candidates(db, limit=30)
            eligible = DuplicateGuardService.filter_unique_candidates(db, site.id, v, candidates, limit=1)
            selected = eligible[0] if eligible else None
            if not selected:
                raise RuntimeError("복지 정책 후보 중 미발행된 신규 후보가 없습니다.")

            external_id = str(selected.external_id)
            enriched = await mod.enrich_item(db, external_id)
            gen = await mod.generate_content(db, enriched)
            art = gen.get("welfare_article")
            rendered_content = mod.render_html(gen)
            title = art.title if art else selected.title
            excerpt = art.excerpt if art else selected.summary
            seo_title = art.seo_title if art else title
            meta_description = art.meta_description if art else excerpt
            tags = art.tags if art else ["복지", "정부지원금", "정책"]
            article_json = art.model_dump_json() if art else "{}"

        elif v == "PRODUCT":
            from app.modules.product.module import ProductModule
            mod = registry.get_module(VerticalType.PRODUCT) or ProductModule()
            candidates = await mod.collect_candidates(db, limit=20)
            eligible = DuplicateGuardService.filter_unique_candidates(db, site.id, v, candidates, limit=1)
            selected = eligible[0] if eligible else None
            if not selected:
                raise RuntimeError("상품 비교 후보 중 미발행된 신규 후보가 없습니다.")

            external_id = str(selected.external_id)
            enriched = await mod.enrich_item(db, external_id)
            gen = await mod.generate_content(db, enriched)
            rendered_content = mod.render_html(gen)
            prod_item = enriched.get("product_item") or enriched.get("product")
            title = f"{prod_item.name} 솔직 스펙 비교 및 실사용자 장단점 총정리" if prod_item else selected.title
            excerpt = f"{prod_item.highlight} - 실제 구매 전 반드시 확인해야 할 핵심 스펙과 가성비 분석." if prod_item else selected.summary
            seo_title = f"{title[:45]} 추천 리뷰"
            meta_description = excerpt[:140]
            tags = ["상품리뷰", "스펙비교", "내돈내산", "쿠팡비교"]
            featured_image_url = getattr(prod_item, "image_url", None) if prod_item else None

        elif v == "NEWS":
            from app.modules.news.module import NewsModule
            mod = registry.get_module(VerticalType.NEWS) or NewsModule()
            candidates = await mod.collect_candidates(db, limit=20)
            eligible = DuplicateGuardService.filter_unique_candidates(db, site.id, v, candidates, limit=1)
            selected = eligible[0] if eligible else None
            if not selected:
                raise RuntimeError("뉴스 팩트체크 후보 중 미발행된 신규 후보가 없습니다.")

            external_id = str(selected.external_id)
            enriched = await mod.enrich_item(db, external_id)
            gen = await mod.generate_content(db, enriched)
            art = gen.get("news_article")
            rendered_content = mod.render_html(gen)
            title = art.title if art else selected.title
            excerpt = art.excerpt if art else selected.summary
            seo_title = art.seo_title if art else title
            meta_description = art.meta_description if art else excerpt
            tags = art.tags if art else ["뉴스", "팩트체크", "시사"]
            article_json = art.model_dump_json() if art else "{}"

        else:
            raise ValueError(f"지원되지 않는 버티컬입니다: {v}")

        # Pre-publish hard check against duplicate titles or topics
        is_unique, dup_reason = DuplicateGuardService.validate_pre_publish(db, site.id, title, rendered_content)
        if not is_unique:
            logger.warning("DuplicateGuard: Aborting publish for site %d: %s", site.id, dup_reason)
            raise RuntimeError(f"발행 차단: {dup_reason}")

        # 2. Publish to WordPress REST API
        publisher = WordPressPublisher(
            site_url=site.site_url,
            username=site.wp_username,
            app_password=site.wp_application_password
        )

        # 2-1. Upload featured image to WordPress media library if available
        featured_media_id = None
        if featured_image_url and isinstance(featured_image_url, str) and featured_image_url.startswith("http"):
            try:
                import httpx
                logger.info("Downloading and uploading featured image for site %d: %s", site.id, featured_image_url)
                async with httpx.AsyncClient(timeout=15.0, verify=False) as http_client:
                    img_res = await http_client.get(featured_image_url)
                    if img_res.status_code == 200 and len(img_res.content) > 500:
                        c_type = img_res.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
                        if not c_type or c_type not in ["image/jpeg", "image/png", "image/webp"]:
                            c_type = "image/jpeg"
                        ext = "jpg" if "jpeg" in c_type else "png" if "png" in c_type else "webp"
                        fn = f"{v.lower()}-cover-{uuid.uuid4().hex[:8]}.{ext}"
                        featured_media_id = await publisher.upload_media(
                            file_bytes=img_res.content,
                            filename=fn,
                            alt_text=f"{title} 대표 이미지",
                            content_type=c_type
                        )
                        logger.info("Featured media uploaded successfully! Media ID: %s", featured_media_id)
            except Exception as e:
                logger.warning("Failed to upload featured image for site %d: %s", site.id, e)

        slug = f"{v.lower()}-{uuid.uuid4().hex[:6]}"
        publish_req = PublishRequest(
            title=title,
            content=rendered_content,
            excerpt=excerpt,
            slug=slug,
            status=PostStatus.PUBLISH,
            categories=[site.vertical],
            tags=tags[:5],
            featured_media_id=featured_media_id
        )

        logger.info("Publishing article to WordPress site: %s (%s)", site.name, site.site_url)
        wp_res = await publisher.publish_post(publish_req)

        # 3. Save to database
        status_val = PostStatusEnum.PUBLISHED.value if wp_res.success else PostStatusEnum.FAILED.value
        post = Post(
            title=title,
            slug=slug,
            rendered_content=rendered_content,
            excerpt=excerpt,
            seo_title=seo_title or title,
            meta_description=meta_description or excerpt,
            vertical=v,
            external_id=external_id,
            movie_id=movie_id,
            site_id=site.id,
            status=status_val,
            quality_status=QualityStatusEnum.PASS.value,
            article_json=article_json,
            published_at=utc_now() if wp_res.success else None,
            wordpress_post_id=wp_res.remote_post_id,
            wordpress_url=wp_res.remote_url or (f"{site.site_url}/?p={wp_res.remote_post_id}" if wp_res.remote_post_id else None),
            failure_reason=wp_res.error_message if not wp_res.success else None
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        summary = f"'{title}' 작성 및 워드프레스 발행 완료 (WP 글 ID: {wp_res.remote_post_id or post.id})"
        logger.info("Single-site automation complete for site %d: %s", site.id, summary)

        # 4. Telegram Notification on Publish
        if wp_res.success:
            try:
                from app.services.telegram_service import TelegramAlertService
                tg = TelegramAlertService()
                if tg.is_configured():
                    pub_url = post.wordpress_url or f"{site.site_url}/?p={wp_res.remote_post_id}"
                    await tg.send_publish_alert(
                        site_name=site.name,
                        title=title,
                        post_url=pub_url,
                        vertical=v,
                        ai_provider=settings.PRIMARY_AI
                    )
            except Exception as tge:
                logger.debug("Telegram publish alert skipped: %s", str(tge))

        return {
            "success": wp_res.success,
            "post_id": post.id,
            "title": title,
            "site_name": site.name,
            "site_url": site.site_url,
            "published_url": post.wordpress_url or site.site_url,
            "summary": summary
        }
