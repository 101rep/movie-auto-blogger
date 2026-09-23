# -*- coding: utf-8 -*-
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Update index.html
html_path = os.path.join(APP_DIR, 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add 1km Live Radius Feed to Home
if '<!-- Real-time 1km Radius Local Pet Feed -->' not in html:
    target = '<!-- Sponsored Hospital & Affiliate Monetization Section'
    radius_feed_section = '''<!-- Real-time 1km Radius Local Pet Feed (실시간 반경 1km 동네 정보 피드) -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-3">
          
          <!-- Feed Header & Location Bar -->
          <div class="flex items-center justify-between border-b border-gray-100 dark:border-neutral-800 pb-2.5">
            <div>
              <div class="flex items-center gap-1.5 font-bold text-sm text-gray-800 dark:text-gray-100">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>내 주변 실시간 펫플레이스</span>
              </div>
              <p class="text-[10px] text-gray-400 mt-0.5">📍 <b class="text-indigo-600 dark:text-indigo-400">서울 강남구 역삼1동</b> 기준 실시간 정보</p>
            </div>
            
            <!-- Refresh Button -->
            <button onclick="refreshRadiusFeed()" id="btn-refresh-feed" class="flex items-center gap-1 px-2.5 py-1.5 bg-gray-100 dark:bg-neutral-800 hover:bg-gray-200 dark:hover:bg-neutral-700 text-gray-700 dark:text-gray-200 rounded-xl text-[11px] font-bold transition-all shadow-sm">
              <i data-lucide="rotate-cw" id="icon-refresh" class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400"></i>
              <span>새로고침</span>
            </button>
          </div>

          <!-- Radius Switcher (1km / 3km / 5km) -->
          <div class="flex items-center justify-between gap-2">
            <span class="text-[11px] font-bold text-gray-500 shrink-0">탐색 반경:</span>
            <div class="flex bg-gray-100 dark:bg-neutral-800 p-1 rounded-xl flex-1 justify-around text-xs">
              <button onclick="changeRadius(1)" id="radius-btn-1" class="radius-btn active flex-1 py-1 rounded-lg font-bold bg-white dark:bg-neutral-700 text-indigo-600 dark:text-indigo-400 shadow-sm transition-all text-center">반경 1km (도보)</button>
              <button onclick="changeRadius(3)" id="radius-btn-3" class="radius-btn flex-1 py-1 rounded-lg font-bold text-gray-500 dark:text-gray-400 transition-all text-center">3km</button>
              <button onclick="changeRadius(5)" id="radius-btn-5" class="radius-btn flex-1 py-1 rounded-lg font-bold text-gray-500 dark:text-gray-400 transition-all text-center">5km</button>
            </div>
          </div>

          <!-- Category Tags Filter -->
          <div class="flex gap-1.5 overflow-x-auto pb-1 scrollbar-none text-[11px]">
            <button onclick="filterRadiusCategory('all')" class="feed-cat active px-2.5 py-1 rounded-lg font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-900/50 shrink-0">전체보기</button>
            <button onclick="filterRadiusCategory('vet')" class="feed-cat px-2.5 py-1 rounded-lg font-bold bg-gray-50 dark:bg-neutral-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-neutral-700 shrink-0">🏥 동물병원</button>
            <button onclick="filterRadiusCategory('cafe')" class="feed-cat px-2.5 py-1 rounded-lg font-bold bg-gray-50 dark:bg-neutral-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-neutral-700 shrink-0">☕ 펫카페/식당</button>
            <button onclick="filterRadiusCategory('school')" class="feed-cat px-2.5 py-1 rounded-lg font-bold bg-gray-50 dark:bg-neutral-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-neutral-700 shrink-0">🎓 유치원/학교</button>
            <button onclick="filterRadiusCategory('grooming')" class="feed-cat px-2.5 py-1 rounded-lg font-bold bg-gray-50 dark:bg-neutral-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-neutral-700 shrink-0">✂️ 미용/용품</button>
          </div>

          <!-- Live Feed Dynamic List -->
          <div id="radius-places-feed" class="space-y-2.5 pt-1 text-xs">
            <!-- Rendered by JS -->
          </div>

        </div>

        <!-- Sponsored Hospital & Affiliate Monetization Section'''
    html = html.replace(target, radius_feed_section)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated index.html with Live Radius Feed successfully')

# 2. Update app.js for Live Radius Logic
js_path = os.path.join(APP_DIR, 'app.js')
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

radius_js = '''
// Live 1km/3km/5km Radius Places Dataset
const radiusDataset = [
  {
    id: 101,
    name: '서울24시 동물의료센터',
    category: 'vet',
    distKm: 0.35,
    distanceStr: '350m (도보 4분)',
    status: '🟢 실시간 진료중 (24시 야간)',
    summary: '슬개골 탈구 전문 • 심야 응급실 상시 운영 • 고양이 친화 인증',
    phone: '02-555-7582',
    icon: '🏥',
    rating: '⭐ 4.9 (리뷰 328)'
  },
  {
    id: 102,
    name: '어반포포 반려견 동반 브런치',
    category: 'cafe',
    distKm: 0.45,
    distanceStr: '450m (도보 6분)',
    status: '🟢 영업중 (~22:00)',
    summary: '실내/테라스 애견동반 • 무료 멍푸치노 제공 • 반려견 수제간식',
    phone: '02-345-1288',
    icon: '☕',
    rating: '⭐ 4.8 (리뷰 214)'
  },
  {
    id: 103,
    name: '도그스쿨 강남 애견 유치원 & 행동교정',
    category: 'school',
    distKm: 0.72,
    distanceStr: '720m (도보 9분)',
    status: '🟢 상담 가능 (~20:00)',
    summary: '전문 훈련사 상주 • 실시간 CCTV 알림장 • 1km 이내 등하원 픽업',
    phone: '02-777-3321',
    icon: '🎓',
    rating: '⭐ 5.0 (리뷰 189)'
  },
  {
    id: 104,
    name: '폼폼 펫 그루밍 & 24시 무인용품샵',
    category: 'grooming',
    distKm: 0.88,
    distanceStr: '880m (도보 11분)',
    status: '🟢 24시 무인영업',
    summary: '저자극 탄산 스파 미용 • 밤샘 급한 사료/패드 키오스크 구매 가능',
    phone: '02-888-1234',
    icon: '✂️',
    rating: '⭐ 4.7 (리뷰 95)'
  },
  {
    id: 105,
    name: '바른 펫 한방 재활 동물병원',
    category: 'vet',
    distKm: 2.1,
    distanceStr: '2.1km (차량 6분)',
    status: '🟢 진료중 (~19:00)',
    summary: '침치료 • 수중 재활 런닝머신 • 노령견 만성질환 케어 전문',
    phone: '02-666-4321',
    icon: '🏥',
    rating: '⭐ 4.9 (리뷰 142)'
  },
  {
    id: 106,
    name: '강남 반려견 힐링 테마파크 & 수영장',
    category: 'school',
    distKm: 4.2,
    distanceStr: '4.2km (차량 12분)',
    status: '🟢 영업중 (~21:00)',
    summary: '1,000평 천연잔디 운동장 • 온수 애견 수영장 • 셀프 목욕실 완비',
    phone: '02-999-5566',
    icon: '🏊',
    rating: '⭐ 4.9 (리뷰 512)'
  }
];

let selectedRadius = 1;
let selectedRadiusCategory = 'all';

function changeRadius(km) {
  selectedRadius = km;
  document.querySelectorAll('.radius-btn').forEach(b => {
    b.classList.remove('active', 'bg-white', 'dark:bg-neutral-700', 'text-indigo-600', 'dark:text-indigo-400', 'shadow-sm');
    b.classList.add('text-gray-500', 'dark:text-gray-400');
  });

  const activeBtn = document.getElementById(`radius-btn-${km}`);
  if (activeBtn) {
    activeBtn.classList.add('active', 'bg-white', 'dark:bg-neutral-700', 'text-indigo-600', 'dark:text-indigo-400', 'shadow-sm');
    activeBtn.classList.remove('text-gray-500', 'dark:text-gray-400');
  }

  refreshRadiusFeed();
}

function filterRadiusCategory(cat) {
  selectedRadiusCategory = cat;
  document.querySelectorAll('.feed-cat').forEach(b => {
    b.classList.remove('active', 'bg-indigo-50', 'dark:bg-indigo-950/60', 'text-indigo-600', 'dark:text-indigo-300', 'border-indigo-200', 'dark:border-indigo-900/50');
    b.classList.add('bg-gray-50', 'dark:bg-neutral-800', 'text-gray-600', 'dark:text-gray-400', 'border-gray-200', 'dark:border-neutral-700');
  });

  event.target.classList.add('active', 'bg-indigo-50', 'dark:bg-indigo-950/60', 'text-indigo-600', 'dark:text-indigo-300', 'border-indigo-200', 'dark:border-indigo-900/50');
  event.target.classList.remove('bg-gray-50', 'dark:bg-neutral-800', 'text-gray-600', 'dark:text-gray-400', 'border-gray-200', 'dark:border-neutral-700');

  renderRadiusFeedList();
}

function refreshRadiusFeed() {
  const icon = document.getElementById('icon-refresh');
  if (icon) icon.classList.add('animate-spin');

  const container = document.getElementById('radius-places-feed');
  if (container) {
    container.innerHTML = `
      <div class="py-6 text-center text-xs text-indigo-600 dark:text-indigo-400 font-bold space-y-1">
        <div class="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p>반경 ${selectedRadius}km 내 최신 펫플레이스 정보를 검색 중...</p>
      </div>
    `;
  }

  setTimeout(() => {
    if (icon) icon.classList.remove('animate-spin');
    renderRadiusFeedList();
  }, 400);
}

function renderRadiusFeedList() {
  const container = document.getElementById('radius-places-feed');
  if (!container) return;

  let filtered = radiusDataset.filter(p => p.distKm <= selectedRadius);
  if (selectedRadiusCategory !== 'all') {
    filtered = filtered.filter(p => p.category === selectedRadiusCategory);
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="p-6 text-center text-gray-400 space-y-1">
        <p class="text-sm font-bold">반경 ${selectedRadius}km 내에 등록된 매장이 없습니다.</p>
        <p class="text-[11px]">상단 탐색 반경을 3km 또는 5km로 넓혀보세요!</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(p => `
    <div class="p-3 bg-gray-50 dark:bg-neutral-800/60 rounded-xl border border-gray-100 dark:border-neutral-800 space-y-2 hover:border-indigo-300 dark:hover:border-indigo-900 transition-colors">
      <div class="flex items-start justify-between">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-white dark:bg-neutral-700 flex items-center justify-center text-base shadow-sm">
            ${p.icon}
          </div>
          <div>
            <div class="flex items-center gap-1.5">
              <h4 class="font-bold text-xs text-gray-900 dark:text-gray-100">${p.name}</h4>
              <span class="text-[10px] text-amber-500 font-bold">${p.rating}</span>
            </div>
            <p class="text-[10px] text-gray-400"><b class="text-indigo-600 dark:text-indigo-400 font-bold">${p.distanceStr}</b> • ${p.status}</p>
          </div>
        </div>
      </div>

      <p class="text-[11px] text-gray-600 dark:text-gray-300 leading-relaxed bg-white dark:bg-neutral-900/60 p-2 rounded-lg border border-gray-100 dark:border-neutral-800">
        ${p.summary}
      </p>

      <div class="flex gap-1.5 pt-0.5">
        <a href="tel:${p.phone}" class="flex-1 py-1.5 bg-white dark:bg-neutral-700 hover:bg-gray-100 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-neutral-600 rounded-lg text-center font-bold text-[10px] flex items-center justify-center gap-1">
          <i data-lucide="phone" class="w-3 h-3"></i>
          <span>전화</span>
        </a>
        <button onclick="openKakaoRoute('${p.name}', '')" class="flex-1 py-1.5 bg-[#FEE500] hover:bg-[#FADA0A] text-[#191919] rounded-lg text-center font-bold text-[10px] flex items-center justify-center gap-1 shadow-sm">
          <span>길찾기</span>
        </button>
      </div>
    </div>
  `).join('');

  lucide.createIcons();
}

// Initial render for radius feed on boot
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(renderRadiusFeedList, 100);
});
'''

if 'function changeRadius(' not in js:
    js += '\n' + radius_js

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print('Updated app.js with Live Radius Feed successfully')