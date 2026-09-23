import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"
style_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\style.css"
app_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\app.js"

# 1. Update style.css with dynamic custom theme palette rules
with open(style_file, 'r', encoding='utf-8') as f:
    css = f.read()

theme_css = """
/* ================= Dynamic Pet Theme Presets ================= */
.theme-sky {
  --theme-color: #3b82f6;
  --theme-color-dark: #2563eb;
  --theme-bg-soft: #eff6ff;
  --theme-border: #bfdbfe;
  --theme-text: #1d4ed8;
}
.theme-pink {
  --theme-color: #f43f5e;
  --theme-color-dark: #e11d48;
  --theme-bg-soft: #fff1f2;
  --theme-border: #fecdd3;
  --theme-text: #be123c;
}
.theme-mint {
  --theme-color: #10b981;
  --theme-color-dark: #059669;
  --theme-bg-soft: #ecfdf5;
  --theme-border: #a7f3d0;
  --theme-text: #047857;
}
.theme-orange {
  --theme-color: #f97316;
  --theme-color-dark: #ea580c;
  --theme-bg-soft: #fff7ed;
  --theme-border: #fed7aa;
  --theme-text: #c2410c;
}
.theme-purple {
  --theme-color: #8b5cf6;
  --theme-color-dark: #7c3aed;
  --theme-bg-soft: #f5f3ff;
  --theme-border: #ddd6fe;
  --theme-text: #6d28d9;
}
.theme-choco {
  --theme-color: #b45309;
  --theme-color-dark: #92400e;
  --theme-bg-soft: #fefce8;
  --theme-border: #fde047;
  --theme-text: #78350f;
}

.theme-target-color {
  color: var(--theme-color, #3b82f6) !important;
}
.theme-target-bg {
  background-color: var(--theme-color, #3b82f6) !important;
}
.theme-target-bg:hover {
  background-color: var(--theme-color-dark, #2563eb) !important;
}
.theme-target-softbg {
  background-color: var(--theme-bg-soft, #eff6ff) !important;
  border-color: var(--theme-border, #bfdbfe) !important;
}
.theme-target-border {
  border-color: var(--theme-color, #3b82f6) !important;
}

.theme-selector-btn.active {
  transform: scale(1.1);
  box-shadow: 0 0 0 3px #ffffff, 0 0 0 5px var(--theme-color, #3b82f6);
}
"""

if '/* ================= Dynamic Pet Theme Presets' not in css:
    css = css + "\n" + theme_css
    with open(style_file, 'w', encoding='utf-8') as f:
        f.write(css)

print("style.css updated with theme presets.")

# 2. Update index.html to add Theme Palette Picker in Pet Profile Modal
with open(index_file, 'r', encoding='utf-8') as f:
    html = f.read()

theme_picker_html = """          <!-- Theme Palette Selection -->
          <div class="space-y-1.5 pt-1">
            <div class="flex items-center justify-between">
              <label class="font-black text-slate-700 block">🎨 나만의 앱 맞춤 테마 컬러</label>
              <span id="theme-preview-name" class="text-[11px] font-bold text-blue-600">스카이블루</span>
            </div>
            <div class="grid grid-cols-6 gap-2 pt-0.5">
              <button type="button" onclick="selectThemePreset('sky', '스카이블루', '#3b82f6')" id="theme-btn-sky" class="theme-selector-btn w-full h-9 rounded-2xl bg-blue-500 shadow-sm transition-all active" title="스카이블루 (산뜻/활발)"></button>
              <button type="button" onclick="selectThemePreset('pink', '러블리 핑크', '#f43f5e')" id="theme-btn-pink" class="theme-selector-btn w-full h-9 rounded-2xl bg-rose-500 shadow-sm transition-all" title="러블리 핑크 (달콤/애교)"></button>
              <button type="button" onclick="selectThemePreset('mint', '포레스트 민트', '#10b981')" id="theme-btn-mint" class="theme-selector-btn w-full h-9 rounded-2xl bg-emerald-500 shadow-sm transition-all" title="포레스트 민트 (편안/자연)"></button>
              <button type="button" onclick="selectThemePreset('orange', '썬샤인 오렌지', '#f97316')" id="theme-btn-orange" class="theme-selector-btn w-full h-9 rounded-2xl bg-orange-500 shadow-sm transition-all" title="썬샤인 오렌지 (개구쟁이)"></button>
              <button type="button" onclick="selectThemePreset('purple', '라벤더 퍼플', '#8b5cf6')" id="theme-btn-purple" class="theme-selector-btn w-full h-9 rounded-2xl bg-violet-500 shadow-sm transition-all" title="라벤더 퍼플 (시크/도도)"></button>
              <button type="button" onclick="selectThemePreset('choco', '밀크 초코', '#b45309')" id="theme-btn-choco" class="theme-selector-btn w-full h-9 rounded-2xl bg-amber-700 shadow-sm transition-all" title="밀크 초코 (포근/클래식)"></button>
            </div>
          </div>"""

# Replace in Pet Profile Modal before Save Button
if '<!-- Theme Palette Selection -->' not in html:
    html = html.replace('<!-- Save Button -->', theme_picker_html + '\n\n        <!-- Save Button -->')

# Add dynamic theme classes to Header logo and Welcome Card
html = html.replace('text-blue-600', 'theme-target-color')
html = html.replace('bg-blue-600', 'theme-target-bg')
html = html.replace('border-blue-400', 'theme-target-border')

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated with theme picker and dynamic theme classes.")

# 3. Update app.js logic to support Theme saving & real-time switching
with open(app_file, 'r', encoding='utf-8') as f:
    js = f.read()

theme_logic_update = """
let currentThemePreset = 'sky';
const themeNames = {
  sky: '스카이블루',
  pink: '러블리 핑크',
  mint: '포레스트 민트',
  orange: '썬샤인 오렌지',
  purple: '라벤더 퍼플',
  choco: '밀크 초코'
};

window.selectThemePreset = function(themeKey, themeLabel, colorCode) {
  currentThemePreset = themeKey;
  const previewName = document.getElementById('theme-preview-name');
  if (previewName) {
    previewName.textContent = themeLabel;
    previewName.style.color = colorCode;
  }

  document.querySelectorAll('.theme-selector-btn').forEach(b => b.classList.remove('active'));
  const activeBtn = document.getElementById(`theme-btn-${themeKey}`);
  if (activeBtn) activeBtn.classList.add('active');

  // Preview theme on container
  applyThemeToContainer(themeKey);
};

function applyThemeToContainer(themeKey) {
  const container = document.getElementById('app-container');
  if (!container) return;

  const allThemes = ['theme-sky', 'theme-pink', 'theme-mint', 'theme-orange', 'theme-purple', 'theme-choco'];
  allThemes.forEach(t => container.classList.remove(t));
  container.classList.add(`theme-${themeKey || 'sky'}`);
}
"""

# Update savePetProfile to store theme
js = js.replace("gender: tempSelectedGender,", "gender: tempSelectedGender,\n    theme: currentThemePreset,")
js = js.replace("currentPet.photoUrl || null;", "currentPet.photoUrl || null;\n  currentThemePreset = currentPet.theme || 'sky';\n  selectThemePreset(currentThemePreset, themeNames[currentThemePreset] || '스카이블루', '#3b82f6');")

# Append theme logic before DOMContentLoaded
if 'let currentThemePreset' not in js:
    js = js + "\n" + theme_logic_update

# Ensure theme is applied on load
js = js.replace("applyPetProfileToUI();", "applyPetProfileToUI();\n  if (currentPet && currentPet.theme) applyThemeToContainer(currentPet.theme);")

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js updated with dynamic theme switching.")
