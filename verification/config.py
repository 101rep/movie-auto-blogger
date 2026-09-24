"""
Configuration for AAOS Playwright Browser Verification Layer
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = BASE_DIR / "data" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_TIMEOUT_MS = 15000  # 15 seconds
HEADLESS = True
VIEWPORT = {"width": 1280, "height": 800}
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
