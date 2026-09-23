# -*- coding: utf-8 -*-
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
KAKAO_JS_KEY = "a0a8a6c45e622ea183ef6fc5ae3f3e5d"
KAKAO_REST_KEY = "c9b0e8bea2b5db7aeb3bca678b0a3d0e"

# 1. Update index.html
html_path = os.path.join(APP_DIR, 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Insert Kakao SDK script tag into <head>
kakao_script_tag = f'<script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}&libraries=services"></script>'

if 'dapi.kakao.com/v2/maps/sdk.js' not in html:
    html = html.replace('<!-- Lucide Icons CDN -->', f'{kakao_script_tag}\n  <!-- Lucide Icons CDN -->')

# Update Map Modal canvas to hold real Kakao Map DOM
old_map_dom_target = '<!-- Interactive Map Visual Simulation (Kakao Map Mockup) -->'
new_map_dom = f'''<!-- Real Interactive Kakao Map Canvas -->
        <div class="relative h-60 bg-slate-100 dark:bg-neutral-800 overflow-hidden shrink-0 border-b border-gray-200 dark:border-neutral-800">
          <div id="kakao-map-container" class="w-full h-full"></div>
          
          <!-- Current Location GPS Button Overlay -->
          <button onclick="getUserGPSLocation()" class="absolute bottom-3 right-3 bg-white dark:bg-neutral-800 text-gray-800 dark:text-gray-200 p-2.5 rounded-full shadow-xl border border-gray-200 dark:border-neutral-700 z-10 hover:scale-105 transition-transform" title="내 위치로 이동">
            <i data-lucide="crosshair" class="w-4 h-4 text-indigo-600 dark:text-indigo-400"></i>
          </button>

          <!-- Map Status Badge -->
          <div class="absolute top-2 left-2 bg-black/70 text-white text-[10px] px-2.5 py-1 rounded-full backdrop-blur z-10 font-bold flex items-center gap-1.5 shadow">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span id="kakao-status-text">카카오 공식 로컬맵 연동됨</span>
          </div>
        </div>'''

if old_map_dom_target in html:
    # Replace mockup map with real kakao map container
    # find section from target to <!-- Place List View -->
    parts = html.split(old_map_dom_target)
    after_parts = parts[1].split('<!-- Place List View -->')
    html = parts[0] + new_map_dom + '\n\n        <!-- Place List View -->' + after_parts[1]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated index.html with Kakao Map SDK script successfully')

# 2. Update app.js
js_path = os.path.join(APP_DIR, 'app.js')
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

kakao_integration_js = f'''
// ==========================================
// 📍 KAKAO MAP OFFICIAL SDK & REAL PLACES API
// ==========================================
const KAKAO_KEY = "{KAKAO_JS_KEY}";
let kakaoMapInstance = null;
let kakaoPlacesService = null;
let currentMarkers = [];
let userCoords = {{ lat: 37.498095, lng: 127.027610, addressName: '서울 강남구 역삼1동' }};

function initKakaoMap() {{
  const container = document.getElementById('kakao-map-container');
  if (!container || typeof kakao === 'undefined' || !kakao.maps) return;

  const options = {{
    center: new kakao.maps.LatLng(userCoords.lat, userCoords.lng),
    level: 4
  }};

  kakaoMapInstance = new kakao.maps.Map(container, options);
  kakaoPlacesService = new kakao.maps.services.Places();

  // Add User Marker
  addUserLocationMarker();

  // Search places around user
  searchKakaoPlacesByFilter();
}}

function addUserLocationMarker() {{
  if (!kakaoMapInstance) return;

  const markerPosition = new kakao.maps.LatLng(userCoords.lat, userCoords.lng);
  const marker = new kakao.maps.Marker({{
    position: markerPosition,
    title: '내 현재 위치'
  }});
  marker.setMap(kakaoMapInstance);

  const infowindow = new kakao.maps.InfoWindow({{
    content: '<div style="padding:4px 8px;font-size:11px;font-weight:bold;color:#4f46e5;">📍 내 위치 (초코네)</div>'
  }});
  infowindow.open(kakaoMapInstance, marker);
}}

function getUserGPSLocation() {{
  if (navigator.geolocation) {{
    navigator.geolocation.getCurrentPosition(
      (position) => {{
        userCoords.lat = position.coords.latitude;
        userCoords.lng = position.coords.longitude;
        if (kakaoMapInstance) {{
          const newCenter = new kakao.maps.LatLng(userCoords.lat, userCoords.lng);
          kakaoMapInstance.setCenter(newCenter);
          addUserLocationMarker();
          searchKakaoPlacesByFilter();
        }}
        alert('📍 현재 GPS 실시간 위치로 중심이 이동되었습니다!');
      }},
      () => {{
        alert('GPS 권한이 필요합니다. 기본 위치(강남구 역삼동)로 탐색합니다.');
      }}
    );
  }}
}}

function searchKakaoPlacesByFilter() {{
  if (!kakaoPlacesService || !kakaoMapInstance) return;

  const queryMap = {{
    all: '동물병원',
    '24h_vet': '24시 동물병원',
    cafe: '애견동반카페',
    park: '반려견 놀이터'
  }};

  const keyword = queryMap[currentMapFilter] || '동물병원';

  const searchOptions = {{
    location: new kakao.maps.LatLng(userCoords.lat, userCoords.lng),
    radius: 3000, // 3km radius
    sort: kakao.maps.services.SortBy.DISTANCE
  }};

  kakaoPlacesService.keywordSearch(keyword, (result, status) => {{
    if (status === kakao.maps.services.Status.OK) {{
      clearMapMarkers();
      renderKakaoPlacesList(result);
    }} else {{
      console.log('Kakao Places fallback triggered');
      renderMapPlacesFallback();
    }}
  }}, searchOptions);
}}

function clearMapMarkers() {{
  currentMarkers.forEach(m => m.setMap(null));
  currentMarkers = [];
}}

function renderKakaoPlacesList(places) {{
  const container = document.getElementById('map-places-container');
  if (!container) return;

  container.innerHTML = places.map((p, idx) => {{
    // Add marker on Kakao Map
    const markerPosition = new kakao.maps.LatLng(p.y, p.x);
    const marker = new kakao.maps.Marker({{
      position: markerPosition,
      map: kakaoMapInstance,
      title: p.place_name
    }});
    currentMarkers.push(marker);

    // Infowindow
    const infowindow = new kakao.maps.InfoWindow({{
      content: `<div style="padding:4px 6px;font-size:10px;font-weight:bold;color:#1e1b4b;">${{p.place_name}}</div>`
    }});
    kakao.maps.event.addListener(marker, 'click', () => {{
      infowindow.open(kakaoMapInstance, marker);
    }});

    const distM = p.distance ? (parseInt(p.distance) < 1000 ? `${{p.distance}}m` : `${{(parseInt(p.distance)/1000).toFixed(1)}}km`) : '가까움';

    return `
      <div class="p-3.5 bg-white dark:bg-neutral-900 rounded-2xl border border-gray-200 dark:border-neutral-800 space-y-2 shadow-sm">
        <div class="flex items-start justify-between">
          <div class="space-y-0.5">
            <div class="flex items-center gap-1.5">
              <span class="text-base">🏥</span>
              <h4 class="font-bold text-xs text-gray-800 dark:text-gray-100">${{p.place_name}}</h4>
            </div>
            <p class="text-[10px] text-gray-400">${{p.road_address_name || p.address_name}} • <b class="text-indigo-600 dark:text-indigo-400 font-bold">${{distM}}</b></p>
          </div>
          <span class="text-[10px] px-2 py-0.5 rounded-full font-bold bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-900/50">
            실시간 카카오 정보
          </span>
        </div>

        <div class="flex flex-wrap gap-1">
          <span class="text-[9px] bg-gray-100 dark:bg-neutral-800 text-gray-600 dark:text-gray-300 px-1.5 py-0.5 rounded">${{p.category_name.split('>').pop().trim()}}</span>
          ${{p.phone ? `<span class="text-[9px] bg-emerald-50 text-emerald-600 px-1.5 py-0.5 rounded">📞 ${{p.phone}}</span>` : ''}}
        </div>

        <div class="pt-2 border-t border-gray-100 dark:border-neutral-800 flex gap-2 text-xs">
          ${{p.phone ? `
            <a href="tel:${{p.phone}}" class="flex-1 py-2 bg-gray-100 dark:bg-neutral-800 hover:bg-gray-200 text-gray-800 dark:text-gray-200 rounded-xl font-bold flex items-center justify-center gap-1 text-[11px]">
              <i data-lucide="phone" class="w-3 h-3"></i>
              <span>전화연결</span>
            </a>
          ` : ''}}
          <a href="${{p.place_url}}" target="_blank" class="flex-1 py-2 bg-[#FEE500] hover:bg-[#FADA0A] text-[#191919] rounded-xl font-bold flex items-center justify-center gap-1 text-[11px] shadow-sm">
            <span>🟡 카카오맵 상세/길찾기</span>
          </a>
        </div>
      </div>
    `;
  }}).join('');

  lucide.createIcons();
}}

function renderMapPlacesFallback() {{
  renderMapPlaces();
}}

// Hook map modal open to initialize Kakao Map
const _oldOpenMapModal = openMapModal;
openMapModal = function() {{
  const modal = document.getElementById('modal-pet-map');
  if (modal) modal.classList.remove('hidden');
  setTimeout(() => {{
    initKakaoMap();
    lucide.createIcons();
  }}, 150);
}};
'''

# Append Kakao Integration Code
js += '\n' + kakao_integration_js

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print('Updated app.js with Kakao SDK Integration successfully')