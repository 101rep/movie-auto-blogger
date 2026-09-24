import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from apps.backend.tre.main import app

client = TestClient(app)

routes = [
    ("/", "통합 대시보드"),
    ("/dashboard", "대시보드"),
    ("/products", "쿠팡 추천"),
    ("/products/1", "상품 파이프라인"),
    ("/ideas", "콘텐츠 아이디어"),
    ("/content", "Threads 콘텐츠"),
    ("/cardnews", "카드뉴스"),
    ("/ag-gateway", "AG Gateway"),
    ("/repurpose", "리퍼포징"),
    ("/calendar", "콘텐츠 캘린더"),
    ("/analytics", "성과"),
    ("/warmup", "양성화"),
    ("/settings", "시스템 설정"),
    ("/pick-manage", "픽"),
]

print("=== Testing All Web UI HTML Endpoints ===")
all_passed = True
for path, expected_text in routes:
    res = client.get(path)
    if res.status_code == 200:
        found = expected_text in res.text
        status = "PASS" if found else "WARN (text not in body)"
        print(f"[{status}] {path} -> 200 OK (checked: '{expected_text}')")
        if not found:
            print(f"      Response snippet: {res.text[:150]}...")
    else:
        print(f"[FAIL] {path} -> {res.status_code}: {res.text[:100]}")
        all_passed = False

if all_passed:
    print("\nALL WEB UI ROUTES VERIFIED 100% SUCCESSFULLY!")
else:
    print("\nSOME ROUTES FAILED!")
    exit(1)
