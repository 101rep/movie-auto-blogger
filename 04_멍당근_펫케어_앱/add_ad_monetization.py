# -*- coding: utf-8 -*-
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Update index.html
html_path = os.path.join(APP_DIR, 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add Sponsored Hospital & Affiliate Cards to Home if not present
if '<!-- Sponsored Hospital & Affiliate Monetization Section -->' not in html:
    target = '<!-- Recent Logs List Preview -->'
    ad_section = '''<!-- Sponsored Hospital & Affiliate Monetization Section (수익화 배너) -->
        <div class="space-y-2.5">
          <!-- 1. Regional Hospital Sponsored Banner (High Revenue B2B) -->
          <div class="bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-2xl p-4 shadow-md relative overflow-hidden border border-blue-700/50">
            <div class="flex items-center justify-between">
              <span class="text-[10px] bg-blue-500/40 text-blue-200 border border-blue-400/40 px-2 py-0.5 rounded-full font-bold">AD • 공식 제휴 병원</span>
              <span class="text-xs text-blue-200">역삼동 1.2km</span>
            </div>
            <div class="mt-2 space-y-1">
              <h4 class="font-bold text-sm">📍 서울24시 동물의료센터 (연중무휴)</h4>
              <p class="text-xs text-blue-200">슬개골 탈구 • 치과 스케일링 • 심야 응급진료</p>
            </div>
            <div class="mt-3 flex gap-2">
              <button onclick="clickAd('hospital_call', '서울24시 동물의료센터')" class="flex-1 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-1 shadow">
                <i data-lucide="phone" class="w-3.5 h-3.5"></i>
                <span>전화 상담</span>
              </button>
              <button onclick="clickAd('hospital_book', '서울24시 동물의료센터')" class="flex-1 py-2 bg-white text-blue-900 font-bold rounded-xl text-xs flex items-center justify-center gap-1 shadow">
                <i data-lucide="calendar" class="w-3.5 h-3.5"></i>
                <span>네이버 예약</span>
              </button>
            </div>
          </div>

          <!-- 2. AI Health-Based Affiliate Commerce Cards (Coupang / Commerce) -->
          <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-2">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5 font-bold text-xs text-gray-800 dark:text-gray-200">
                <span class="text-amber-500">🛒</span>
                <span>초코의 건강 데이터 맞춤 추천 (제휴)</span>
              </div>
              <span class="text-[10px] text-gray-400">광고 제휴</span>
            </div>

            <div class="grid grid-cols-2 gap-2">
              <div onclick="clickAd('commerce', '가수분해 저알러지 사료')" class="p-2.5 bg-gray-50 dark:bg-neutral-800/60 rounded-xl border border-gray-100 dark:border-neutral-800 cursor-pointer hover:border-indigo-500 transition-colors">
                <div class="w-full h-16 bg-amber-50 dark:bg-amber-950/40 rounded-lg flex items-center justify-center text-2xl mb-1.5">
                  🥩
                </div>
                <span class="text-[10px] text-rose-500 font-bold">피부/가려움 케어</span>
                <p class="font-bold text-xs text-gray-800 dark:text-gray-200 line-clamp-1">닥터힐스 저알러지 사료 2kg</p>
                <div class="flex items-center justify-between mt-1">
                  <span class="text-xs font-black text-indigo-600 dark:text-indigo-400">32,000원</span>
                  <span class="text-[10px] bg-rose-50 dark:bg-rose-950 text-rose-600 px-1 rounded font-bold">최저가 ></span>
                </div>
              </div>

              <div onclick="clickAd('commerce', '슬개골 관절 영양제')" class="p-2.5 bg-gray-50 dark:bg-neutral-800/60 rounded-xl border border-gray-100 dark:border-neutral-800 cursor-pointer hover:border-indigo-500 transition-colors">
                <div class="w-full h-16 bg-blue-50 dark:bg-blue-950/40 rounded-lg flex items-center justify-center text-2xl mb-1.5">
                  💊
                </div>
                <span class="text-[10px] text-indigo-500 font-bold">말티즈 필수 관절</span>
                <p class="font-bold text-xs text-gray-800 dark:text-gray-200 line-clamp-1">조인트케어 글루코사민 60정</p>
                <div class="flex items-center justify-between mt-1">
                  <span class="text-xs font-black text-indigo-600 dark:text-indigo-400">28,500원</span>
                  <span class="text-[10px] bg-rose-50 dark:bg-rose-950 text-rose-600 px-1 rounded font-bold">최저가 ></span>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. Pet Insurance Comparison CPA Banner -->
          <div onclick="clickAd('insurance', '3세 말티즈 맞춤 펫보험 비교')" class="bg-gradient-to-r from-emerald-600 to-teal-700 text-white rounded-2xl p-3.5 shadow cursor-pointer hover:opacity-95 transition-all flex items-center justify-between">
            <div class="space-y-0.5">
              <span class="text-[10px] bg-white/20 px-2 py-0.5 rounded-full font-bold">💰 병원비 최대 90% 보장</span>
              <h4 class="font-black text-sm">초코(3세) 맞춤 펫보험 다이렉트 비교</h4>
              <p class="text-[11px] text-emerald-100">슬개골 수술비 • 하루 통원비 한눈에 견적 확인하기</p>
            </div>
            <i data-lucide="chevron-right" class="w-6 h-6 shrink-0 text-emerald-200"></i>
          </div>
        </div>

        <!-- Recent Logs List Preview -->'''
    html = html.replace(target, ad_section)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated index.html with Monetization Banners successfully')

# 2. Update app.js for ad click simulation
js_path = os.path.join(APP_DIR, 'app.js')
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

ad_js = '''
// Ad & Affiliate Monetization Action Handlers
function clickAd(type, title) {
  if (type === 'hospital_call') {
    alert(`📞 [동물병원 전화 연결]\\n${title} (02-555-7582) 직통 전화로 연결합니다.`);
  } else if (type === 'hospital_book') {
    alert(`📅 [네이버 예약 페이지 이동]\\n${title} 실시간 진료 예약 페이지로 이동합니다.`);
  } else if (type === 'commerce') {
    alert(`🛒 [제휴 파트너스 최저가 쇼핑몰 연결]\\n'${title}' 상품 페이지로 이동합니다.\\n(구매 시 앱 운영 수익 5% 자동 적립)`);
  } else if (type === 'insurance') {
    alert(`💰 [다이렉트 펫보험 비교 견적]\\n초코(말티즈, 3세) 맞춤형 슬개골/구토/피부 보장 비교 견적 페이지로 연결됩니다.`);
  }
}
'''

if 'function clickAd(' not in js:
    js += '\n' + ad_js

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print('Updated app.js with clickAd successfully')