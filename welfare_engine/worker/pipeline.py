"""Welfare Pipeline Controller for Welfare Engine V1.0.
Coordinates the end-to-end autonomous publishing lifecycle:
1. Data Ingestion (Collector Agent)
2. Policy Evaluation & Scoring (Evaluator Agent)
3. Dynamic Volume Decision (Day 1-7: 3/day; Day 8+: 1~3/day based on Grade A count)
4. Multi-Persona Routing (Persona Router)
5. Structured Article Generation (Writer Agent)
6. 1080x1080 Card News Generation (Image Generator)
7. WordPress Post Scheduling (Publisher)
8. Post Existence & Status Verification (Verifier Agent)
9. Daily Operational Reporting (Telegram Reporter)
"""
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import func

from welfare_engine.config import settings, WELFARE_BLOGS, WelfareBlogConfig
from welfare_engine.database.session import SessionLocal
from welfare_engine.database.models import (
    WelfareContent, WelfarePublication, ContentStatus, PriorityLevel
)
from welfare_engine.agent.collector import WelfareDataCollector
from welfare_engine.agent.evaluator import WelfareEvaluator
from welfare_engine.agent.persona_router import WelfarePersonaRouter, PersonaDispatchPlan
from welfare_engine.agent.writer import WelfareWriterAgent
from welfare_engine.agent.image_generator import WelfareCardNewsGenerator
from welfare_engine.agent.verifier import WelfareVerifierAgent
from welfare_engine.publisher.wordpress_publisher import WordPressWelfarePublisher
from welfare_engine.reporter.telegram_reporter import WelfareTelegramReporter

logger = logging.getLogger("welfare_engine.pipeline")


class WelfarePipelineController:
    """Orchestrates 24-hour autonomous welfare publishing."""

    def __init__(
        self,
        collector: Optional[WelfareDataCollector] = None,
        evaluator: Optional[WelfareEvaluator] = None,
        router: Optional[WelfarePersonaRouter] = None,
        writer: Optional[WelfareWriterAgent] = None,
        image_gen: Optional[WelfareCardNewsGenerator] = None,
        verifier: Optional[WelfareVerifierAgent] = None,
        reporter: Optional[WelfareTelegramReporter] = None
    ):
        self.collector = collector or WelfareDataCollector()
        self.evaluator = evaluator or WelfareEvaluator()
        self.router = router or WelfarePersonaRouter()
        self.writer = writer or WelfareWriterAgent()
        self.image_gen = image_gen or WelfareCardNewsGenerator()
        self.reporter = reporter or WelfareTelegramReporter()
        self.verifier = verifier or WelfareVerifierAgent(self.reporter)

    def determine_daily_target_quota(self, days_since_launch: int = 1) -> int:
        """Determine daily publishing volume per blog based on operational stage and material quality."""
        # Initial 7 days: fixed 3 posts per blog (total 9)
        if days_since_launch <= settings.INITIAL_DAYS:
            logger.info(f"Initial Phase (Day {days_since_launch}): Fixed quota of 3 posts per blog.")
            return settings.INITIAL_DAILY_POSTS_PER_BLOG

        # Stabilized stage (Day 8+): dynamically adjust based on Grade A materials (score >= 80)
        db = SessionLocal()
        try:
            grade_a_count = db.query(WelfareContent).filter(
                WelfareContent.priority_score >= 80,
                WelfareContent.status == ContentStatus.READY.value
            ).count()

            if grade_a_count >= 5:
                quota = 3
            elif grade_a_count >= 2:
                quota = 2
            elif grade_a_count >= 1:
                quota = 1
            else:
                quota = 0 # No forced writing when quality material is lacking
            logger.info(f"Stabilized Phase (Day {days_since_launch}): Found {grade_a_count} Grade-A candidates. Quota set to {quota}/blog.")
            return quota
        finally:
            db.close()

    def get_schedule_times(self, target_date: date, count: int) -> List[datetime]:
        """Compute exact schedule times for posts on a given date."""
        if count == 3:
            slots = settings.SLOTS_3_POSTS
        elif count == 2:
            slots = settings.SLOTS_2_POSTS
        elif count == 1:
            slots = settings.SLOTS_1_POST
        else:
            return []

        times = []
        for slot in slots:
            hh, mm = map(int, slot.split(":"))
            dt = datetime(target_date.year, target_date.month, target_date.day, hh, mm, 0)
            times.append(dt)
        return times

    async def run_pipeline(
        self,
        target_date: Optional[date] = None,
        days_since_launch: int = 1,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Execute full daily autonomous pipeline."""
        exec_date = target_date or date.today()
        logger.info(f"=== Starting Welfare Publishing Pipeline for {exec_date} (Day {days_since_launch}) ===")

        # 1. Ingestion Phase
        raw_items = await self.collector.collect_all(limit=20)
        saved_items = self.collector.save_to_database(raw_items)
        logger.info(f"[Step 1] Ingested {len(raw_items)} items, saved {len(saved_items)} new candidates.")

        # 2. Evaluation Phase
        db = SessionLocal()
        try:
            unevaluated = db.query(WelfareContent).filter(
                WelfareContent.status == ContentStatus.NEW.value
            ).all()
            for item in unevaluated:
                self.evaluator.evaluate_and_update(item)
            db.commit()
            logger.info(f"[Step 2] Evaluated {len(unevaluated)} candidates.")
        finally:
            db.close()

        # 3. Determine Quota
        quota = self.determine_daily_target_quota(days_since_launch=days_since_launch)
        schedule_times = self.get_schedule_times(exec_date, quota)

        report_stats: Dict[str, Dict[str, int]] = {
            "BLOG_A": {"scheduled": quota, "success": 0},
            "BLOG_B": {"scheduled": quota, "success": 0},
            "BLOG_C": {"scheduled": quota, "success": 0}
        }
        report_errors: List[Dict[str, str]] = []

        if quota == 0:
            logger.info("Quality materials insufficient today. Skipping generation per Quality-First mandate.")
            await self.reporter.send_daily_report(report_stats, report_errors, report_date=str(exec_date))
            return {"status": "SUCCESS", "published_count": 0, "message": "No Grade-A materials today"}

        # 4. Publishing & Verification Phase per Blog
        for blog_key, blog in WELFARE_BLOGS.items():
            logger.info(f"--- Processing {blog.name} ({blog_key}) - Target Quota: {quota} ---")
            publisher = WordPressWelfarePublisher(blog)

            db = SessionLocal()
            try:
                # Find top READY candidates that haven't been published to this blog yet
                candidates = db.query(WelfareContent).filter(
                    WelfareContent.status == ContentStatus.READY.value,
                    ~WelfareContent.published_blog.contains(blog_key)
                ).order_by(WelfareContent.priority_score.desc()).limit(quota).all()

                logger.info(f"[{blog_key}] Selected {len(candidates)} candidates for generation.")

                for idx, cand in enumerate(candidates):
                    scheduled_time = schedule_times[idx] if idx < len(schedule_times) else datetime.now() + timedelta(hours=2)

                    try:
                        # 4.1 Route to persona angle
                        all_plans = self.router.route(cand)
                        blog_plan = next((p for p in all_plans if p.blog_key == blog_key), None)
                        if not blog_plan:
                            # Fallback plan if router didn't generate one
                            blog_plan = PersonaDispatchPlan(
                                blog_key=blog_key,
                                blog_config=blog,
                                angle=f"{blog.persona_name} 관점 안내",
                                title=f"[{blog.name}] {cand.title} 핵심 정리",
                                lead_intro=blog.sample_phrases[0],
                                target_focus=cand.target or "대한민국 국민",
                                faq_focus="신청자격 및 지원혜택"
                            )

                        # 4.2 Write article data
                        article_data = await self.writer.generate_article_data(cand, blog_plan)
                        final_title = article_data.get("title", blog_plan.title)
                        content_html = self.writer.render_html(article_data, blog_plan)

                        # 4.3 Generate card news thumbnail
                        image_path = self.image_gen.generate_card_news(
                            content=cand,
                            blog=blog,
                            custom_title=final_title
                        )

                        if dry_run:
                            logger.info(f"[DRY-RUN] Would publish '{final_title}' to {blog.name} at {scheduled_time}")
                            report_stats[blog_key]["success"] += 1
                            continue

                        # 4.4 Publish to WordPress
                        category_name = cand.category or blog.categories[0]
                        tags = article_data.get("tags", [category_name, blog.name, "정부지원금"])
                        is_imm = cand.priority_level == PriorityLevel.IMMEDIATE.value

                        pub_res = await publisher.publish_article(
                            title=final_title,
                            content_html=content_html,
                            category_name=category_name,
                            tags=tags,
                            image_path=image_path,
                            scheduled_at=scheduled_time,
                            is_immediate=is_imm
                        )

                        if not pub_res.get("success"):
                            raise RuntimeError(pub_res.get("error", "WordPress publish failed"))

                        post_id = pub_res["post_id"]
                        post_url = pub_res["post_url"]

                        # 4.5 Record in DB
                        publication = WelfarePublication(
                            content_id=cand.id,
                            blog_key=blog_key,
                            site_id=blog.site_id,
                            persona_title=final_title,
                            wp_post_id=post_id,
                            wp_url=post_url,
                            wp_status=pub_res.get("post_status", "future"),
                            featured_media_id=pub_res.get("media_id"),
                            scheduled_at=scheduled_time,
                            verification_status="PENDING"
                        )
                        db.add(publication)
                        db.commit()
                        db.refresh(publication)

                        # 4.6 Verification Agent Check
                        verified = await self.verifier.verify_and_record(
                            publication=publication,
                            blog=blog,
                            expected_status="publish" if is_imm else "future"
                        )
                        db.commit()

                        if verified:
                            report_stats[blog_key]["success"] += 1
                            # Update candidate's published_blog record
                            curr_blogs = [b for b in cand.published_blog.split(",") if b]
                            if blog_key not in curr_blogs:
                                curr_blogs.append(blog_key)
                                cand.published_blog = ",".join(curr_blogs)
                            cand.status = ContentStatus.PUBLISHED.value
                            db.commit()
                        else:
                            report_errors.append({
                                "blog_name": blog.name,
                                "title": final_title,
                                "reason": publication.error_message or "검증 실패",
                                "status": "재시도 대기"
                            })

                    except Exception as e:
                        logger.error(f"Error publishing cand [{cand.id}] to {blog.name}: {e}")
                        report_errors.append({
                            "blog_name": blog.name,
                            "title": cand.title,
                            "reason": str(e),
                            "status": "오류 기록"
                        })
            finally:
                db.close()

        # 5. Telegram Daily Operational Report
        if not dry_run:
            await self.reporter.send_daily_report(
                stats=report_stats,
                errors=report_errors,
                report_date=str(exec_date)
            )

        logger.info(f"=== Welfare Publishing Pipeline Completed for {exec_date} ===")
        return {
            "status": "SUCCESS",
            "stats": report_stats,
            "errors_count": len(report_errors)
        }
