import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"
app_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\app.js"

with open(index_file, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Head with Leaflet and Kakao Map
leaflet_snippet = """  <!-- Leaflet Map CSS/JS (Instant Real Map Engine Fallback) -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <!-- Kakao Map SDK -->
  <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey=a0a8a6c45e622ea183ef6fc5ae3f3e5d&libraries=services&autoload=false"></script>"""

if 'leaflet@1.9.4' not in html:
    if '//dapi.kakao.com/v2/maps/sdk.js' in html:
        old_kakao = '<script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=a0a8a6c45e622ea183ef6fc5ae3f3e5d&libraries=services"></script>'
        html = html.replace(old_kakao, leaflet_snippet)
    elif '<!-- Kakao Map SDK -->' in html:
        html = html.replace('<!-- Kakao Map SDK -->', leaflet_snippet)

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated.")

# 2. Update app.js map logic
with open(app_file, 'r', encoding='utf-8') as f:
    js = f.read()

new_map_logic = """// Enhanced Real Map Engine (Kakao Map + Leaflet OpenStreetMap Hybrid)
let leafletMapInstance = null;
let kakaoMapInstance = null;

const userLat = 37.498095;
const userLng = 127.027610;

const placesMapData = [
  { id: 101, name: '서울24시 동물의료센터', category: 'vet', lat: 37.499500, lng: 127.028900, distKm: 0.35, distanceStr: '350m', status: '🟢 24시 야간응급', phone: '02-555-7582', icon: '🏥', address: '서울 강남구 역삼동 642-1' },
  { id: 102, name: '어반포포 반려견 동반 브런치', category: 'cafe', lat: 37.496500, lng: 127.029800, distKm: 0.45, distanceStr: '450m', status: '🟢 영업중 (~22:00)', phone: '02-345-1288', icon: '☕', address: '서울 강남구 역삼동 650-2' },
  { id: 103, name: '도그스쿨 강남 애견 유치원 & 행동교정', category: 'school', lat: 37.495000, lng: 127.025500, distKm: 0.72, distanceStr: '720m', status: '🟢 상담가능 (~20:00)', phone: '02-777-3321', icon: '🎓', address: '서울 강남구 역삼동 700-15' },
  { id: 104, name: '폼폼 펫 그루밍 & 24시 무인용품샵', category: 'grooming', lat: 37.502000, lng: 127.024000, distKm: 0.88, distanceStr: '880m', status: '🟢 24시 무인영업', phone: '02-888-1234', icon: '✂️', address: '서울 강남구 역삼동 610-8' },
  { id: 105, name: '바른 펫 한방 재활 동물병원', category: 'vet', lat: 37.510000, lng: 127.035000, distKm: 2.1, distanceStr: '2.1km', status: '🟢 진료중 (~19:00)', phone: '02-666-4321', icon: '🏥', address: '서울 강남구 논현동 112-4' },
  { id: 106, name: '강남 반려견 힐링 테마파크 & 수영장', category: 'school', lat: 37.480000, lng: 127.050000, distKm: 4.2, distanceStr: '4.2km', status: '🟢 영업중 (~21:00)', phone: '02-999-5566', icon: '🏊', address: '서울 강남구 개포동 188-3' }
];

window.openMapModal = function() {
  const modal = document.getElementById('modal-pet-map');
  if (modal) {
    modal.classList.remove('hidden');
    renderModalPlacesList();
    setTimeout(() => {
      initRealPetMap();
      if (window.lucide) lucide.createIcons();
    }, 150);
  }
};

window.closeMapModal = function() {
  const modal = document.getElementById('modal-pet-map');
  if (modal) modal.classList.add('hidden');
};

function renderModalPlacesList() {
  const container = document.getElementById('map-places-container');
  if (!container) return;

  container.innerHTML = `
    <div class="flex items-center justify-between pb-1">
      <span class="text-xs font-black text-gray-900 dark:text-white">📍 내 주변 실시간 탐색 (${placesMapData.length}곳)</span>
      <span class="text-[11px] text-indigo-600 dark:text-indigo-400 font-bold">반경 1km 안심존</span>
    </div>
    ${placesMapData.map(p => `
      <div class="p-3 bg-gray-50 dark:bg-neutral-800/80 rounded-2xl border border-gray-100 dark:border-neutral-700/60 flex items-center justify-between hover:border-indigo-500 transition-all">
        <div class="flex items-center gap-2.5">
          <div class="w-10 h-10 rounded-xl bg-white dark:bg-neutral-700 flex items-center justify-center text-xl shadow-sm border border-gray-100 dark:border-neutral-600">
            ${p.icon}
          </div>
          <div>
            <div class="flex items-center gap-1.5">
              <h4 class="font-bold text-xs text-gray-900 dark:text-white">${p.name}</h4>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 font-bold">${p.distanceStr}</span>
            </div>
            <p class="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium mt-0.5">${p.status}</p>
            <p class="text-[10px] text-gray-400">${p.address}</p>
          </div>
        </div>
        <div class="flex gap-1.5 shrink-0">
          <a href="tel:${p.phone}" class="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800" title="전화">
            <i data-lucide="phone" class="w-3.5 h-3.5"></i>
          </a>
          <button onclick="openKakaoRoute('${p.name}', '${p.address}')" class="px-2.5 py-1.5 rounded-xl bg-indigo-600 text-white font-bold text-[11px] flex items-center gap-1 shadow-sm hover:bg-indigo-700">
            <i data-lucide="navigation" class="w-3 h-3"></i>
            <span>길찾기</span>
          </button>
        </div>
      </div>
    `).join('')}
  `;
}

function initRealPetMap() {
  const container = document.getElementById('kakao-map-container');
  if (!container) return;

  // Always initialize Leaflet immediately to guarantee instant visible map render!
  initLeafletMap(container);

  // If Kakao maps SDK is loaded and authorized, try upgrading to Kakao Map
  if (window.kakao && window.kakao.maps) {
    try {
      window.kakao.maps.load(function() {
        try {
          const mapOption = {
            center: new window.kakao.maps.LatLng(userLat, userLng),
            level: 4
          };
          container.innerHTML = '';
          const map = new window.kakao.maps.Map(container, mapOption);
          kakaoMapInstance = map;

          // User Marker
          const userMarker = new window.kakao.maps.Marker({
            position: new window.kakao.maps.LatLng(userLat, userLng),
            map: map
          });
          const userOverlay = new window.kakao.maps.CustomOverlay({
            position: new window.kakao.maps.LatLng(userLat, userLng),
            content: '<div style="background:#4f46e5;color:#fff;padding:3px 8px;border-radius:12px;font-size:11px;font-weight:bold;box-shadow:0 2px 6px rgba(0,0,0,0.3);">📍 초코네 (내 위치)</div>',
            yAnchor: 2.2
          });
          userOverlay.setMap(map);

          // Place Markers
          placesMapData.forEach(p => {
            const marker = new window.kakao.maps.Marker({
              position: new window.kakao.maps.LatLng(p.lat, p.lng),
              map: map
            });
            const info = new window.kakao.maps.InfoWindow({
              content: `<div style="padding:6px 10px;font-size:11px;font-weight:bold;color:#111;min-width:140px;">${p.icon} ${p.name}<br><span style="font-size:10px;color:#4f46e5;">${p.distanceStr} • ${p.status}</span></div>`
            });
            window.kakao.maps.event.addListener(marker, 'click', function() {
              info.open(map, marker);
            });
          });
        } catch(e) {
          console.warn('Kakao map initialization fallback to Leaflet');
          initLeafletMap(container);
        }
      });
    } catch(e) {
      console.warn('Kakao map load failed, using Leaflet');
    }
  }
}

function initLeafletMap(container) {
  if (typeof L === 'undefined') {
    container.innerHTML = '<div class="w-full h-full flex flex-col items-center justify-center text-xs text-gray-400 p-4 text-center"><span>지도 엔진 로드 중...</span></div>';
    return;
  }

  container.innerHTML = '<div id="leaflet-pet-map" style="width:100%; height:100%; z-index:1;"></div>';
  const mapEl = document.getElementById('leaflet-pet-map');
  
  if (leafletMapInstance) {
    try {
      leafletMapInstance.remove();
    } catch(e) {}
    leafletMapInstance = null;
  }

  const map = L.map(mapEl, {
    zoomControl: false,
    attributionControl: false
  }).setView([userLat, userLng], 15);

  leafletMapInstance = map;

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
  }).addTo(map);

  // User Circle & Marker (1km Radius Safe Zone)
  L.circle([userLat, userLng], {
    color: '#4f46e5',
    fillColor: '#6366f1',
    fillOpacity: 0.15,
    radius: 1000
  }).addTo(map);

  // User Marker
  const userIcon = L.divIcon({
    className: 'custom-user-marker',
    html: '<div style="background:#4f46e5;color:white;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 3px 8px rgba(0,0,0,0.4);border:2px solid white;">🐕</div>',
    iconSize: [34, 34],
    iconAnchor: [17, 17]
  });

  L.marker([userLat, userLng], { icon: userIcon })
    .addTo(map)
    .bindPopup('<b>📍 초코네 (내 위치)</b><br><span style="font-size:11px;color:#666;">서울 강남구 역삼1동 (반경 1km 안심존)</span>')
    .openPopup();

  // Facility Markers
  placesMapData.forEach(p => {
    const pinIcon = L.divIcon({
      className: 'custom-place-marker',
      html: `<div style="background:#ffffff;color:#111;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;box-shadow:0 3px 8px rgba(0,0,0,0.3);border:2px solid #4f46e5;cursor:pointer;">${p.icon}</div>`,
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });

    L.marker([p.lat, p.lng], { icon: pinIcon })
      .addTo(map)
      .bindPopup(`
        <div style="font-size:12px;min-width:160px;padding:2px;">
          <div style="font-weight:bold;color:#111;">${p.icon} ${p.name}</div>
          <div style="font-size:10px;color:#10b981;font-weight:600;margin-top:2px;">${p.status}</div>
          <div style="font-size:10px;color:#4f46e5;margin-top:2px;">거리: ${p.distanceStr}</div>
          <div style="margin-top:8px;display:flex;gap:4px;">
            <a href="tel:${p.phone}" style="padding:4px 8px;background:#10b981;color:white;border-radius:6px;font-size:10px;text-decoration:none;font-weight:bold;">📞 전화</a>
            <a href="https://map.kakao.com/link/search/${encodeURIComponent(p.name)}" target="_blank" style="padding:4px 8px;background:#4f46e5;color:white;border-radius:6px;font-size:10px;text-decoration:none;font-weight:bold;">🗺️ 카카오 길찾기</a>
          </div>
        </div>
      `);
  });

  setTimeout(() => {
    map.invalidateSize();
  }, 200);
}

window.getUserGPSLocation = function() {
  if (leafletMapInstance) {
    leafletMapInstance.setView([userLat, userLng], 15);
  } else if (kakaoMapInstance && window.kakao) {
    kakaoMapInstance.setCenter(new window.kakao.maps.LatLng(userLat, userLng));
  }
  alert('📍 현재 위치(서울 강남구 역삼1동)로 지도를 이동했습니다.');
};
"""

# Replace in app.js
start_marker = "// 6. Kakao Map Modal Functions"
end_marker = "// 7. Doctor Chart"

if start_marker in js and end_marker in js:
    before = js.split(start_marker)[0]
    after = js.split(end_marker)[1]
    new_js = before + start_marker + "\n" + new_map_logic + "\n" + end_marker + after
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_js)
    print("app.js updated successfully with hybrid map engine!")
else:
    print("Markers not found, writing to app.js")
