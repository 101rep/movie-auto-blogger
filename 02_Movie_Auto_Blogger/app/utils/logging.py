"""Structured logging configuration with log rotation and secret masking."""
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from typing import Optional
from app.utils.security import sanitize_sensitive_text


class SensitiveDataFilter(logging.Filter):
    """Filter that intercepts and masks sensitive tokens in log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = sanitize_sensitive_text(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: (sanitize_sensitive_text(v) if isinstance(v, str) else v)
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    sanitize_sensitive_text(v) if isinstance(v, str) else v
                    for v in record.args
                )
        return True


def setup_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """Configure structured logging with file rotation and console output."""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Avoid duplicate handlers if setup is called multiple times
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        filter_sensitive = SensitiveDataFilter()

        # Rotating File Handler
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(filter_sensitive)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)

        # Stream Handler (Stdout) with UTF-8 / safe encoding
        if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.addFilter(filter_sensitive)
        stream_handler.setLevel(numeric_level)
        root_logger.addHandler(stream_handler)

    logger = logging.getLogger("movie_auto_blogger")
    logger.info("Logging initialized with level: %s", log_level)
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance prefixed with the application namespace."""
    base_name = "movie_auto_blogger"
    return logging.getLogger(f"{base_name}.{name}" if name else base_name)
