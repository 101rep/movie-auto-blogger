import os
import shutil
import sys
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

base = r"C:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티"
desktop = r"C:\Users\ktaeh\OneDrive\바탕 화면"

print("==================================================")
print("🚀 [안티그래비티] 폴더 정리 & 삭제 & 재구조화 시작")
print("==================================================")

# --- STEP 1: 불필요한 ZIP 파일 및 캐시/스크래치/구버전 삭제 ---
zip_files_to_delete = [
    "ToonForge_Antigravity_v0.3.zip",
    "ToonForge_Desktop_Studio_v2.0.zip",
    "naver-blog-seo-optimizer.zip",
    "ToonForge_GPT.zip",
    "ToonForge_Gemini.zip",
    "movie_auto_blogger_handoff.zip",
]

loose_files_to_delete = [
    "scratch_edge_history.db",
    "scratch_youtube_details.json",
    "scratch_youtube_meta.json",
    "test_loader.html",
    "proxy_8080.py",
    "create_lnk.ps1",
    "run_daemon.sh",
    "ToonForge_Desktop_PRD.md",
    "ToonForge_Master_PRD_for_GPT.md",
    "ToonForge_실행하기.bat",
    "툰포지_스튜디오_실행.bat",
    "무비오토블로거_실행.bat",
    "인스타보너스_실행하기.bat",
]

dirs_to_delete = [
    "ToonForge_Antigravity_v0.3",
    "ToonForge_GPT",
    "ToonForge_Gemini",
    "imagipark-main",
    ".pytest_cache",
    "__pycache__",
]

print("\n1. 불필요한 ZIP 파일 삭제 중...")
for zf in zip_files_to_delete:
    target = os.path.join(base, zf)
    if os.path.exists(target):
        sz = os.path.getsize(target) / (1024 * 1024)
        os.remove(target)
        print(f"  ✓ 삭제 완료 (ZIP): {zf} ({sz:.1f} MB)")

print("\n2. 임시 캐시 및 불필요한 파일 삭제 중...")
for lf in loose_files_to_delete:
    target = os.path.join(base, lf)
    if os.path.exists(target):
        sz = os.path.getsize(target) / 1024
        os.remove(target)
        print(f"  ✓ 삭제 완료: {lf} ({sz:.1f} KB)")

print("\n3. 구버전 및 중복 폴더 삭제 중...")
for d in dirs_to_delete:
    target = os.path.join(base, d)
    if os.path.exists(target):
        shutil.rmtree(target, ignore_errors=True)
        print(f"  ✓ 폴더 삭제 완료: {d}")

# --- STEP 2: 5대 전용 프로그램 폴더 생성 ---
f1 = os.path.join(base, "[01] Threads_쿠팡_자동화")
f2 = os.path.join(base, "[02] Movie_Auto_Blogger")
f3 = os.path.join(base, "[03] ToonForge_스튜디오")
f4 = os.path.join(base, "[04] 멍당근_펫케어_앱")
f5 = os.path.join(base, "[05] 결과물_및_문서")

for f in [f1, f2, f3, f4, f5]:
    os.makedirs(f, exist_ok=True)

print("\n4. 5대 전용 프로그램 폴더 생성 완료:")
print(f"  📁 {os.path.basename(f1)}")
print(f"  📁 {os.path.basename(f2)}")
print(f"  📁 {os.path.basename(f3)}")
print(f"  📁 {os.path.basename(f4)}")
print(f"  📁 {os.path.basename(f5)}")

# --- STEP 3: 프로그램별 폴더로 이동 ---
print("\n5. 파일 및 폴더를 각 전용 위치로 이동 중...")

# 5-1. [02] Movie_Auto_Blogger 이동
src_movie = os.path.join(base, "movie-auto-blogger")
if os.path.exists(src_movie) and os.path.abspath(src_movie) != os.path.abspath(f2):
    # Move contents
    for item in os.listdir(src_movie):
        src_item = os.path.join(src_movie, item)
        dst_item = os.path.join(f2, item)
        if not os.path.exists(dst_item):
            shutil.move(src_item, dst_item)
    shutil.rmtree(src_movie, ignore_errors=True)
    print("  ✓ [02] Movie_Auto_Blogger 이동 완료")

# 5-2. [03] ToonForge_스튜디오 이동
src_toon = os.path.join(base, "ToonForge_Desktop_Windows")
if os.path.exists(src_toon) and os.path.abspath(src_toon) != os.path.abspath(f3):
    for item in os.listdir(src_toon):
        src_item = os.path.join(src_toon, item)
        dst_item = os.path.join(f3, item)
        if not os.path.exists(dst_item):
            shutil.move(src_item, dst_item)
    shutil.rmtree(src_toon, ignore_errors=True)
    print("  ✓ [03] ToonForge_스튜디오 이동 완료")

# 5-3. [04] 멍당근_펫케어_앱 이동
src_pet = os.path.join(base, "PetCare_App")
if os.path.exists(src_pet) and os.path.abspath(src_pet) != os.path.abspath(f4):
    for item in os.listdir(src_pet):
        src_item = os.path.join(src_pet, item)
        dst_item = os.path.join(f4, item)
        if not os.path.exists(dst_item):
            shutil.move(src_item, dst_item)
    shutil.rmtree(src_pet, ignore_errors=True)
    print("  ✓ [04] 멍당근_펫케어_앱 이동 완료")

# 펫케어 실행 배치파일 및 서버 동기화 배치파일 이동
for pet_bat in ["펫케어_앱_실행하기.bat", "멍당근_서버_동기화.bat"]:
    p_src = os.path.join(base, pet_bat)
    if os.path.exists(p_src):
        shutil.move(p_src, os.path.join(f4, pet_bat))
        print(f"  ✓ {pet_bat} -> [04] 멍당근_펫케어_앱 이동 완료")

# 5-4. [05] 결과물_및_문서 이동
for doc_item in ["인스타_샘플_결과물", "docs", "SYSTEM_MANUAL.md"]:
    d_src = os.path.join(base, doc_item)
    if os.path.exists(d_src):
        dst = os.path.join(f5, doc_item)
        if not os.path.exists(dst):
            shutil.move(d_src, dst)
        print(f"  ✓ {doc_item} -> [05] 결과물_및_문서 이동 완료")

# 5-5. [01] Threads_쿠팡_자동화로 이동할 항목들
threads_dirs = [
    "app", "components", "data", "database", "integrations",
    "services", "scripts", "utils", "prompts", "agents",
    "domain_types", "tests", "browser_sessions"
]

threads_files = [
    ".env", ".env.example", "config.py", "threads_coupang.db",
    "worker.py", "requirements.txt", "pytest.ini",
    "trendspot24_stitch_custom.css", "cloudflared.exe",
    "start_threads_automation.bat", "start_server.bat", "run_tests.bat",
    "가상직원3명_스튜디오_실행.bat", "텔레그램_중간직원_실행.bat",
    "서버_원클릭_동기화.bat", "서버에서_최신받기.bat"
]

for td in threads_dirs:
    td_src = os.path.join(base, td)
    if os.path.exists(td_src) and td_src != f1:
        dst = os.path.join(f1, td)
        if not os.path.exists(dst):
            shutil.move(td_src, dst)
        print(f"  ✓ 폴더 이동: {td} -> [01] Threads_쿠팡_자동화")

for tf in threads_files:
    tf_src = os.path.join(base, tf)
    if os.path.exists(tf_src):
        dst = os.path.join(f1, tf)
        if not os.path.exists(dst):
            shutil.move(tf_src, dst)
        print(f"  ✓ 파일 이동: {tf} -> [01] Threads_쿠팡_자동화")

print("\n전체 이동 및 정리 단계 완료!")
