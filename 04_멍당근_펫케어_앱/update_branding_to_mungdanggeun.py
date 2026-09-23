import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"
app_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\app.js"
manifest_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\manifest.json"
bat_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\펫케어_앱_실행하기.bat"
guide_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\구글플레이_출시_가이드.md"

# 1. Update index.html
with open(index_file, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace title and branding
html = html.replace('<title>펫로그 AI (PetLog AI) - 1초 무료 AI 건강진단 & 멍냥궁합 & 스마트 차트</title>', '<title>멍당근 - 동네 펫용품 나눔 & 1초 무료 AI 건강진단 & 펫케어</title>')
html = html.replace('<h1 id="header-title" class="text-xl font-black tracking-tight theme-target-color">petlog</h1>', '<h1 id="header-title" class="text-xl font-black tracking-tight text-orange-600">멍당근</h1>')
html = html.replace('<h1 id="header-title" class="text-2xl font-black tracking-tight theme-target-color">petlog</h1>', '<h1 id="header-title" class="text-xl font-black tracking-tight text-orange-600">멍당근</h1>')
html = html.replace('petlog', '멍당근')
html = html.replace('펫로그 AI', '멍당근')
html = html.replace('펫로그', '멍당근')

# Update icon next to header logo to carrot 🥕
html = html.replace('<span class="text-2xl animate-gentle">🐾</span>', '<span class="text-2xl animate-gentle">🥕</span>')

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated with 멍당근 branding.")

# 2. Update app.js
with open(app_file, 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace("home: '펫로그 AI',", "home: '멍당근',")
js = js.replace("펫로그 AI", "멍당근")
js = js.replace("펫로그", "멍당근")
js = js.replace("petlog", "멍당근")

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js updated with 멍당근 branding.")

# 3. Update manifest.json
if os.path.exists(manifest_file):
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = f.read()
    manifest = manifest.replace("펫로그 AI", "멍당근")
    manifest = manifest.replace("펫로그", "멍당근")
    manifest = manifest.replace("PetLog AI", "멍당근")
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write(manifest)
    print("manifest.json updated.")

# 4. Update bat file
if os.path.exists(bat_file):
    with open(bat_file, 'r', encoding='utf-8') as f:
        bat = f.read()
    bat = bat.replace("펫로그 AI (PetLog AI)", "멍당근 (동네 펫용품 나눔 & 펫케어)")
    with open(bat_file, 'w', encoding='utf-8') as f:
        f.write(bat)
    print("bat launcher updated.")

# 5. Update guide file
if os.path.exists(guide_file):
    with open(guide_file, 'r', encoding='utf-8') as f:
        guide = f.read()
    guide = guide.replace("펫로그 AI", "멍당근")
    guide = guide.replace("펫로그", "멍당근")
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    print("guide updated.")
