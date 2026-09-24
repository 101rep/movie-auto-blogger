"""Service for reading and updating operational settings in database and runtime cache."""
import re
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.models import AppSetting
from app.utils.logging import get_logger

logger = get_logger("settings_service")

TIME_REGEX = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class SettingsService:
    """Manages operational settings persistence and runtime synchronization."""

    SUPPORTED_KEYS = {
        "daily_post_count",
        "candidate_pool_size",
        "publish_time_1",
        "publish_time_2",
        "publish_time_3",
        "publish_time_4",
        "auto_publish",
        "primary_ai",
        "fallback_ai",
        "openai_model",
        "gemini_model",
        "media_upload_enabled",
        "wordpress_url",
        "wordpress_username",
        "wordpress_app_password",
        "telegram_bot_token",
        "telegram_chat_id",
    }

    def get_all_settings(self, db: Session) -> Dict[str, Any]:
        """Fetch all operational settings merged from DB and runtime defaults."""
        settings = get_settings()
        db_records = db.execute(select(AppSetting)).scalars().all()
        db_map = {item.key: item.value for item in db_records}

        return {
            "daily_post_count": int(db_map.get("daily_post_count", settings.DAILY_POST_COUNT)),
            "candidate_pool_size": int(db_map.get("candidate_pool_size", settings.CANDIDATE_POOL_SIZE)),
            "publish_time_1": db_map.get("publish_time_1", settings.PUBLISH_TIME_1),
            "publish_time_2": db_map.get("publish_time_2", settings.PUBLISH_TIME_2),
            "publish_time_3": db_map.get("publish_time_3", settings.PUBLISH_TIME_3),
            "publish_time_4": db_map.get("publish_time_4", settings.PUBLISH_TIME_4),
            "auto_publish": db_map.get("auto_publish", str(settings.AUTO_PUBLISH)).lower() == "true",
            "primary_ai": db_map.get("primary_ai", settings.PRIMARY_AI),
            "fallback_ai": db_map.get("fallback_ai", settings.FALLBACK_AI),
            "openai_model": db_map.get("openai_model", settings.OPENAI_MODEL),
            "gemini_model": db_map.get("gemini_model", settings.GEMINI_MODEL),
            "media_upload_enabled": db_map.get("media_upload_enabled", str(settings.MEDIA_UPLOAD_ENABLED)).lower() == "true",
            "wordpress_url": db_map.get("wordpress_url", settings.WORDPRESS_URL or ""),
            "wordpress_username": db_map.get("wordpress_username", settings.WORDPRESS_USERNAME or ""),
            "has_wordpress_app_password": bool(db_map.get("wordpress_app_password") or settings.WORDPRESS_APPLICATION_PASSWORD),
            "telegram_bot_token": db_map.get("telegram_bot_token", settings.TELEGRAM_BOT_TOKEN or ""),
            "telegram_chat_id": db_map.get("telegram_chat_id", settings.TELEGRAM_CHAT_ID or ""),
            "timezone": settings.APP_TIMEZONE,
        }

    def update_settings(self, db: Session, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate, persist in DB, and synchronize with runtime settings."""
        settings = get_settings()

        for key, val in updates.items():
            if key not in self.SUPPORTED_KEYS:
                continue

            str_val = str(val).strip()

            # Validation
            if key == "daily_post_count":
                try:
                    num = int(str_val)
                    if not (1 <= num <= 10):
                        raise ValueError("하루 발행 수는 1~10편 사이여야 합니다.")
                    str_val = str(num)
                    settings.DAILY_POST_COUNT = num
                except ValueError as e:
                    raise ValueError(f"잘못된 daily_post_count: {e}")

            elif key == "candidate_pool_size":
                try:
                    num = int(str_val)
                    if not (5 <= num <= 50):
                        raise ValueError("후보군 수집 풀은 5~50편 사이여야 합니다.")
                    str_val = str(num)
                    settings.CANDIDATE_POOL_SIZE = num
                except ValueError as e:
                    raise ValueError(f"잘못된 candidate_pool_size: {e}")

            elif key in ("publish_time_1", "publish_time_2", "publish_time_3", "publish_time_4"):
                if not TIME_REGEX.match(str_val):
                    raise ValueError(f"{key}는 'HH:MM' 형식이어야 합니다. (예: 08:30)")
                if key == "publish_time_1":
                    settings.PUBLISH_TIME_1 = str_val
                elif key == "publish_time_2":
                    settings.PUBLISH_TIME_2 = str_val
                elif key == "publish_time_3":
                    settings.PUBLISH_TIME_3 = str_val
                elif key == "publish_time_4":
                    settings.PUBLISH_TIME_4 = str_val

            elif key == "auto_publish":
                b_val = str_val.lower() in ("true", "1", "yes", "on")
                str_val = "true" if b_val else "false"
                settings.AUTO_PUBLISH = b_val

            elif key == "media_upload_enabled":
                b_val = str_val.lower() in ("true", "1", "yes", "on")
                str_val = "true" if b_val else "false"
                settings.MEDIA_UPLOAD_ENABLED = b_val

            elif key in ("primary_ai", "fallback_ai"):
                low = str_val.lower()
                if low not in ("openai", "gemini"):
                    raise ValueError(f"{key}는 'openai' 또는 'gemini'여야 합니다.")
                str_val = low
                if key == "primary_ai":
                    settings.PRIMARY_AI = low
                else:
                    settings.FALLBACK_AI = low

            elif key == "openai_model":
                settings.OPENAI_MODEL = str_val

            elif key == "gemini_model":
                settings.GEMINI_MODEL = str_val

            elif key == "wordpress_url":
                if str_val and not (str_val.startswith("http://") or str_val.startswith("https://")):
                    raise ValueError("워드프레스 URL은 http:// 또는 https:// 로 시작해야 합니다.")
                settings.WORDPRESS_URL = str_val or None

            elif key == "wordpress_username":
                settings.WORDPRESS_USERNAME = str_val or None

            elif key == "wordpress_app_password":
                clean_pw = str_val.replace(" ", "")
                if clean_pw:
                    settings.WORDPRESS_APPLICATION_PASSWORD = clean_pw
                    str_val = clean_pw
                else:
                    # Do not overwrite with empty if existing password is set and user submitted blank
                    continue

            elif key == "telegram_bot_token":
                settings.TELEGRAM_BOT_TOKEN = str_val or None

            elif key == "telegram_chat_id":
                settings.TELEGRAM_CHAT_ID = str_val or None

            # Upsert into AppSetting
            record = db.execute(select(AppSetting).where(AppSetting.key == key)).scalar_one_or_none()
            if record:
                record.value = str_val
            else:
                db.add(AppSetting(key=key, value=str_val))

        db.commit()
        logger.info("Operational settings updated successfully: %s", list(updates.keys()))
        return self.get_all_settings(db)

    def toggle_auto_publish(self, db: Session) -> bool:
        """Toggle AUTO_PUBLISH setting on/off and return new state."""
        current = self.get_all_settings(db)["auto_publish"]
        new_state = not current
        self.update_settings(db, {"auto_publish": new_state})
        logger.info("Auto-publish toggled: %s -> %s", current, new_state)
        return new_state
