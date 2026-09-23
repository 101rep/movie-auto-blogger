# -*- coding: utf-8 -*-
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Update index.html
html_path = os.path.join(APP_DIR, 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add Map Banner in Home if not present
if '<!-- Nearby Pet Map Quick Access Banner -->' not in html:
    target = '<!-- AI Pet Compatibility & Social Banner -->'
    map_banner = '''<!-- Nearby Pet Map Quick Access Banner (카카오맵/구글맵 연동) -->
        <div onclick="openMapModal()" class="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white rounded-2xl p-4 cursor-pointer shadow-md hover:opacity-95 transition-all flex items-center justify-between relative overflow-hidden">
          <div class="space-y-1 z-10">
            <div class="flex items-center gap-1 text-[11px] font-bold bg-white/20 w-fit px-2 py-0.5 rounded-full">
              <span>📍 카카오맵 연동</span>
              <span>• 실시간 내 주변 탐색</span>
            </div>
            <h3 class="font-black text-base">내 주변 24시 동물병원 & 펫플레이스</h3>
            <p class="text-xs text-blue-100">야간 응급 진료 병원, 동반 카페, 운동장 1초 길찾기</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center text-2xl shrink-0 z-10">
            🗺️
          </div>
        </div>

        <!-- AI Pet Compatibility & Social Banner -->'''
    html = html.replace(target, map_banner)

# Add Map Modal in index.html if not present
if 'id="modal-pet-map"' not in html:
    map_modal_code = '''
    <!-- Modal: Nearby Pet Map & 24h Vet Clinic Explorer -->
    <div id="modal-pet-map" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-md bg-white dark:bg-neutral-900 h-full sm:h-[90vh] sm:rounded-3xl flex flex-col border border-gray-200 dark:border-neutral-800 animate-slide-up overflow-hidden text-left">
        
        <!-- Header -->
        <div class="px-4 py-3 border-b border-gray-100 dark:border-neutral-800 flex items-center justify-between shrink-0">
          <div class="flex items-center gap-2">
            <span class="text-xl">🗺️</span>
            <div>
              <h3 class="font-bold text-sm">내 주변 펫 지도</h3>
              <p class="text-[10px] text-gray-400">현재 위치: 서울시 강남구 역삼동 기준</p>
            </div>
          </div>
          <button onclick="closeMapModal()" class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>

        <!-- Map Filter Category Pills -->
        <div class="px-4 py-2 bg-gray-50 dark:bg-neutral-800/50 flex gap-1.5 overflow-x-auto shrink-0 scrollbar-none border-b border-gray-100 dark:border-neutral-800">
          <button onclick="filterMapCategory('all')" id="map-pill-all" class="map-pill active px-3 py-1.5 rounded-full text-xs font-bold bg-indigo-600 text-white whitespace-nowrap">전체</button>
          <button onclick="filterMapCategory('24h_vet')" id="map-pill-24h" class="map-pill px-3 py-1.5 rounded-full text-xs font-bold bg-gray-200 dark:bg-neutral-700 text-gray-700 dark:text-gray-300 whitespace-nowrap">🚨 24시 응급병원</button>
          <button onclick="filterMapCategory('cafe')" id="map-pill-cafe" class="map-pill px-3 py-1.5 rounded-full text-xs font-bold bg-gray-200 dark:bg-neutral-700 text-gray-700 dark:text-gray-300 whitespace-nowrap">☕ 동반 카페/식당</button>
          <button onclick="filterMapCategory('park')" id="map-pill-park" class="map-pill px-3 py-1.5 rounded-full text-xs font-bold bg-gray-200 dark:bg-neutral-700 text-gray-700 dark:text-gray-300 whitespace-nowrap">🌳 애견 운동장</button>
        </div>

        <!-- Interactive Map Visual Simulation (Kakao Map Mockup) -->
        <div class="relative h-56 bg-slate-200 dark:bg-neutral-800 overflow-hidden shrink-0 border-b border-gray-200 dark:border-neutral-800 flex items-center justify-center">
          <div class="absolute inset-0 opacity-40 dark:opacity-20 bg-[radial-gradient(#4f46e5_1px,transparent_1px)] [background-size:16px_16px]"></div>
          
          <!-- Mock Pins on Map -->
          <div class="absolute top-8 left-16 text-center cursor-pointer hover:scale-110 transition-transform">
            <div class="px-2 py-1 bg-red-600 text-white text-[10px] font-bold rounded-md shadow-lg flex items-center gap-1">
              <span>🚨 24시 서울동물의료센터</span>
            </div>
            <span class="text-2xl">📍</span>
          </div>

          <div class="absolute bottom-10 right-20 text-center cursor-pointer hover:scale-110 transition-transform">
            <div class="px-2 py-1 bg-amber-600 text-white text-[10px] font-bold rounded-md shadow-lg flex items-center gap-1">
              <span>☕ 멍멍파크 카페</span>
            </div>
            <span class="text-2xl">📍</span>
          </div>

          <div class="absolute top-12 right-12 text-center cursor-pointer hover:scale-110 transition-transform">
            <div class="px-2 py-1 bg-emerald-600 text-white text-[10px] font-bold rounded-md shadow-lg flex items-center gap-1">
              <span>🌳 역삼 반려견 놀이터</span>
            </div>
            <span class="text-2xl">📍</span>
          </div>

          <!-- My Location Pin -->
          <div class="text-center z-10">
            <div class="w-6 h-6 rounded-full bg-blue-600 border-2 border-white shadow-lg animate-pulse flex items-center justify-center text-[10px] text-white">
              나
            </div>
          </div>

          <!-- Map Provider Badge -->
          <div class="absolute bottom-2 left-2 bg-black/60 text-white text-[9px] px-2 py-0.5 rounded backdrop-blur">
            Powered by Kakao & Google Map
          </div>
        </div>

        <!-- Place List View -->
        <div class="flex-1 overflow-y-auto p-4 space-y-2.5" id="map-places-container">
          <!-- Rendered by JS -->
        </div>

      </div>
    </div>
'''
    html = html.replace('<!-- Modal: AI Pet Compatibility', map_modal_code + '\n    <!-- Modal: AI Pet Compatibility')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated index.html with Map Features successfully')

# 2. Update app.js for Map Logic
js_path = os.path.join(APP_DIR, 'app.js')
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

map_js = '''
// Pet Map Places Data
const petPlaces = [
  {
    id: 1,
    name: '서울24시 동물의료센터',
    category: '24h_vet',
    badge: '🚨 24시 연중무휴 응급',
    distance: '350m (도보 5분)',
    address: '서울 강남구 역삼로 142',
    phone: '02-555-7582',
    tags: ['슬개골 전문', '심야 야간할증 안내', '고양이 대기실 분리'],
    icon: '🏥'
  },
  {
    id: 2,
    name: '강남 24시 펫종합병원',
    category: '24h_vet',
    badge: '🚨 24시 응급 수술센터',
    distance: '820m (차량 3분)',
    address: '서울 강남구 테헤란로 204',
    phone: '02-567-9911',
    tags: ['CT/MRI 정밀검진', '치과 스케일링', '응급 입원실'],
    icon: '🏥'
  },
  {
    id: 3,
    name: '어반포포 반려견 동반 브런치 카페',
    category: 'cafe',
    badge: '☕ 실내/야외 동반 가능',
    distance: '450m (도보 7분)',
    address: '서울 강남구 논현로 98길',
    phone: '02-345-1288',
    tags: ['멍푸치노 무료', '인조잔디 테라스', '기저귀 무료제공'],
    icon: '☕'
  },
  {
    id: 4,
    name: '역삼 도심형 반려견 놀이터 & 공원',
    category: 'park',
    badge: '🌳 대형/소형견 분리 운동장',
    distance: '620m (도보 9분)',
    address: '서울 강남구 역삼동 산 12',
    phone: '02-3423-6250',
    tags: ['무료 입장', '어질리티 놀이기구', '음수대 완비'],
    icon: '🌳'
  }
];

let currentMapFilter = 'all';

function openMapModal() {
  const modal = document.getElementById('modal-pet-map');
  if (modal) modal.classList.remove('hidden');
  renderMapPlaces();
  lucide.createIcons();
}

function closeMapModal() {
  const modal = document.getElementById('modal-pet-map');
  if (modal) modal.classList.add('hidden');
}

function filterMapCategory(cat) {
  currentMapFilter = cat;
  document.querySelectorAll('.map-pill').forEach(b => {
    b.classList.remove('active', 'bg-indigo-600', 'text-white');
    b.classList.add('bg-gray-200', 'dark:bg-neutral-700', 'text-gray-700', 'dark:text-gray-300');
  });

  const activeBtn = document.getElementById(`map-pill-${cat === 'all' ? 'all' : cat === '24h_vet' ? '24h' : cat}`);
  if (activeBtn) {
    activeBtn.classList.add('active', 'bg-indigo-600', 'text-white');
    activeBtn.classList.remove('bg-gray-200', 'dark:bg-neutral-700', 'text-gray-700', 'dark:text-gray-300');
  }

  renderMapPlaces();
}

function renderMapPlaces() {
  const container = document.getElementById('map-places-container');
  if (!container) return;

  const list = currentMapFilter === 'all' ? petPlaces : petPlaces.filter(p => p.category === currentMapFilter);

  container.innerHTML = list.map(p => `
    <div class="p-3.5 bg-white dark:bg-neutral-900 rounded-2xl border border-gray-200 dark:border-neutral-800 space-y-2 shadow-sm">
      <div class="flex items-start justify-between">
        <div class="space-y-0.5">
          <div class="flex items-center gap-1.5">
            <span class="text-base">${p.icon}</span>
            <h4 class="font-bold text-xs text-gray-800 dark:text-gray-100">${p.name}</h4>
          </div>
          <p class="text-[10px] text-gray-400">${p.address} • <b class="text-indigo-600 dark:text-indigo-400">${p.distance}</b></p>
        </div>
        <span class="text-[10px] px-2 py-0.5 rounded-full font-bold ${p.category === '24h_vet' ? 'bg-red-50 dark:bg-red-950/50 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-900/50' : 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400'}">
          ${p.badge}
        </span>
      </div>

      <div class="flex flex-wrap gap-1">
        ${p.tags.map(t => `<span class="text-[9px] bg-gray-100 dark:bg-neutral-800 text-gray-600 dark:text-gray-300 px-1.5 py-0.5 rounded">${t}</span>`).join('')}
      </div>

      <div class="pt-2 border-t border-gray-100 dark:border-neutral-800 flex gap-2 text-xs">
        <a href="tel:${p.phone}" class="flex-1 py-2 bg-gray-100 dark:bg-neutral-800 hover:bg-gray-200 text-gray-800 dark:text-gray-200 rounded-xl font-bold flex items-center justify-center gap-1 text-[11px]">
          <i data-lucide="phone" class="w-3 h-3"></i>
          <span>전화연결</span>
        </a>
        <button onclick="openKakaoRoute('${p.name}', '${p.address}')" class="flex-1 py-2 bg-[#FEE500] hover:bg-[#FADA0A] text-[#191919] rounded-xl font-bold flex items-center justify-center gap-1 text-[11px] shadow-sm">
          <span>🟡 카카오맵 길찾기</span>
        </button>
      </div>
    </div>
  `).join('');

  lucide.createIcons();
}

function openKakaoRoute(name, address) {
  const kakaoUrl = `https://map.kakao.com/link/search/${encodeURIComponent(name)}`;
  window.open(kakaoUrl, '_blank');
}
'''

if 'function openMapModal()' not in js:
    js += '\n' + map_js

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print('Updated app.js with Map Logic successfully')