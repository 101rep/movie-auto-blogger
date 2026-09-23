import sys
import os
from pathlib import Path
import uvicorn

# Setup python path to include 00_Central_AI_Manager and root
CENTRAL_DIR = Path(__file__).resolve().parent.parent
if str(CENTRAL_DIR) not in sys.path:
    sys.path.insert(0, str(CENTRAL_DIR))

ROOT_DIR = CENTRAL_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from nexus_command.config import nexus_settings
from nexus_command.api.server import app

def main():
    print("=" * 64)
    print(f"  🚀 [{nexus_settings.APP_NAME} v{nexus_settings.APP_VERSION}]")
    print(f"  {nexus_settings.APP_SUBTITLE}")
    print("=" * 64)
    print(f"  • 메신저 웹 주소: http://{nexus_settings.NEXUS_HOST}:{nexus_settings.NEXUS_PORT}")
    print(f"  • Gemini 두뇌 엔진: {nexus_settings.GEMINI_MODEL}")
    print(f"  • 8대 블로그 & 7대 스레드 Asset Registry 탑재 완료")
    print("=" * 64)

    uvicorn.run(
        app,
        host=nexus_settings.NEXUS_HOST,
        port=nexus_settings.NEXUS_PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()
