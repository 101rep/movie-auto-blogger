import asyncio
import time
import logging
from datetime import datetime
from database.connection import SessionLocal
from services.scheduler_service import SchedulerService
from services.analytics_service import AnalyticsService
from services.learning_service import LearningService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] Worker: %(message)s")
logger = logging.getLogger("BackgroundWorker")

async def run_worker_loop(interval_seconds: int = 60):
    """
    Continuous background loop that:
    1. Checks and publishes due scheduled posts
    2. Syncs analytics metrics
    3. Runs AI learning loop
    """
    logger.info("Threads Auto-Scheduler Background Worker started.")
    # Allow FastAPI server to finish binding port and answering requests first
    await asyncio.sleep(2)
    counter = 0

    while True:
        def _sync_work(curr_counter: int):
            db = SessionLocal()
            try:
                sched_svc = SchedulerService(db)
                analytics_svc = AnalyticsService(db)
                learning_svc = LearningService(db)

                # 1. Process Due Scheduled Posts
                published_ids = sched_svc.process_due_schedules()
                if published_ids:
                    logger.info(f"Successfully auto-published {len(published_ids)} posts: IDs {published_ids}")
                    # Auto-pin the published product to the account's PICK page
                    try:
                        from services.pick_sourcer import PickSourcerService
                        from database.models import Content
                        for pid in published_ids:
                            content = db.query(Content).filter(Content.id == pid).first()
                            if content and content.account_id and content.product_id:
                                PickSourcerService.pin_product_for_account(db, content.account_id, content.product_id)
                                logger.info(f"Auto-pinned product {content.product_id} to Account {content.account_id} PICK page!")
                    except Exception as pin_err:
                        logger.warning(f"Auto-pin error: {pin_err}")

                # 2. Every 10 minutes (counter % 10 == 0), sync metrics & run learning & warmup evaluation
                if curr_counter % 10 == 0:
                    report = analytics_svc.get_summary_report()
                    insight = learning_svc.analyze_and_learn()
                    logger.info(f"Self-Learning Cycle Complete: Best Angle [{insight.best_angle}], Total Revenue: {insight.total_revenue}원")
                    try:
                        from services.warmup_evaluator import WarmupEvaluationService
                        warmup_svc = WarmupEvaluationService(db)
                        warmup_svc.evaluate_and_sync_all()
                    except Exception as w_err:
                        logger.warning(f"Warmup evaluation cycle error: {w_err}")

                # 3. Every 2 minutes (counter % 2 == 0), check comments and auto-reply
                if curr_counter % 2 == 0:
                    try:
                        from services.reply_service import ReplyEngineService
                        reply_svc = ReplyEngineService(db)
                        replies_sent = reply_svc.process_all_accounts()
                        if replies_sent:
                            logger.info(f"Auto-replied to {len(replies_sent)} follower comments: {replies_sent}")
                    except Exception as reply_err:
                        logger.warning(f"Reply engine cycle error: {reply_err}")

                # 4. Every 5 minutes (counter % 5 == 0), check and run scheduled outbound warmup (1일 10건 자연 분산 소통)
                if curr_counter % 5 == 0:
                    try:
                        from services.outbound_service import OutboundInteractionService
                        outbound_res = OutboundInteractionService.process_scheduled_outbound_for_accounts(db)
                        if outbound_res.get("dispatched_count", 0) > 0:
                            logger.info(f"Scheduled Outbound Warmup dispatched {outbound_res['dispatched_count']} interactions: {outbound_res['dispatched']}")
                    except Exception as outbound_err:
                        logger.warning(f"Scheduled outbound cycle error: {outbound_err}")

            finally:
                db.close()

        try:
            await asyncio.to_thread(_sync_work, counter)
        except Exception as e:
            logger.error(f"Error in background worker loop: {e}")

        counter += 1
        await asyncio.sleep(interval_seconds)

if __name__ == "__main__":
    asyncio.run(run_worker_loop(interval_seconds=30))