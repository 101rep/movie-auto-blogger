// ==========================================
// 🏡 [PET SITTER SPECIALIZED APP - JAVASCRIPT CORE]
// 펫케어 메이트 - 전문 펫시터 매칭 & 돌봄 관리
// ==========================================

// Global State
let currentTab = 'home';
let currentSitterFilter = 'all';
let currentBookingFilter = 'active';
let currentSelectedSitter = null;
let bookingWizardStep = 1;
let bookingDraft = {
  sitterId: null,
  service: 'visit',
  date: '',
  time: '14:00',
  petName: '초코',
  memo: ''
};

// 1. Mock Data: Pet Profile & Care Card
let petProfile = {
  name: '초코',
  breed: '말티즈',
  age: 3,
  gender: '남아 (중성화 O)',
  weight: 3.4,
  feedMemo: '아침 9시 건사료 50g + 유산균 1포 급여',
  medicine: '닭고기 알러지 주의, 관절 영양제 1알',
  walkNotes: '다른 강아지 보면 짖음 주의, 하네스 앞섬 잡기',
  hospital: '역삼 24시 동물의료센터 (02-1234-5678)',
  emergency: '010-9876-5432'
};

// 2. Mock Data: Professional Pet Sitters Database
const SITTERS_DATA = [
  {
    id: 1,
    name: '이지은 펫시터',
    avatar: '👩‍⚕️',
    title: '반려견행동지도사 1급 • 5년차',
    rating: 4.98,
    reviewsCount: 128,
    location: '역삼1동',
    distanceKm: 0.8,
    services: ['visit', 'walk', 'daycare'],
    pricePerUnit: 25000,
    priceUnitStr: '방문 30분당 25,000원',
    sizeSupport: ['small', 'medium'],
    badge: '🏆 이달의 베스트',
    intro: '안녕하세요! 5년 차 반려견행동지도사 이지은입니다. 아이의 성향에 맞춘 스트레스 제로 안심 방문 돌봄과 안전 산책을 약속드립니다.',
    experience: '동물병원 간호사 2년, 전문 펫시터 3년 (누적 400회+ 돌봄)',
    availableTimes: '월~일 08:00 ~ 21:00'
  },
  {
    id: 2,
    name: '박준혁 펫시터',
    avatar: '👨‍⚕️',
    title: '전문 훈련사 • 대형견 전문',
    rating: 4.95,
    reviewsCount: 89,
    location: '역삼2동',
    distanceKm: 1.4,
    services: ['walk', 'visit', 'overnight'],
    pricePerUnit: 28000,
    priceUnitStr: '산책 60분당 28,000원',
    sizeSupport: ['small', 'medium', 'large'],
    badge: '⭐ 대형견 마스터',
    intro: '에너지 넘치는 아이들을 위한 맞춤형 파워 산책 및 분리불안 완화 놀이 전문입니다. 대형견도 안심하고 맡겨주세요.',
    experience: '애견훈련소 코치 4년, 전문 산책 매니저',
    availableTimes: '월~토 07:00 ~ 22:00'
  },
  {
    id: 3,
    name: '김서연 펫시터',
    avatar: '👩‍🦰',
    title: '노령견 케어 전문 • 반려동물관리사',
    rating: 5.0,
    reviewsCount: 64,
    location: '도곡동',
    distanceKm: 2.1,
    services: ['visit', 'daycare', 'overnight'],
    pricePerUnit: 30000,
    priceUnitStr: '방문 60분당 30,000원',
    sizeSupport: ['small'],
    badge: '💖 노령견 안심 케어',
    intro: '투약이 필요한 아이, 노령견의 정성스러운 식사 보조 및 실내 마사지 케어를 전문으로 합니다.',
    experience: '반려동물관리사 1급, 노령견 호스피스 이수',
    availableTimes: '화~일 10:00 ~ 20:00'
  }
];

// 3. Mock Data: Bookings
let bookings = [
  {
    id: 101,
    sitterId: 1,
    sitterName: '이지은 펫시터',
    serviceTitle: '🏠 방문 돌봄 (30분)',
    date: '2026-09-22',
    time: '14:00 ~ 14:30',
    petName: '초코',
    price: 25000,
    status: 'confirmed', // confirmed, ongoing, completed
    statusLabel: '예약 확정',
    memo: '사료 50g 급여 및 실내 놀이 부탁드립니다.'
  },
  {
    id: 100,
    sitterId: 2,
    sitterName: '박준혁 펫시터',
    serviceTitle: '🦮 안심 산책 (60분)',
    date: '2026-09-18',
    time: '18:00 ~ 19:00',
    petName: '초코',
    price: 28000,
    status: 'completed',
    statusLabel: '돌봄 완료',
    memo: '역삼공원 코스 산책 완료'
  }
];

// 4. Mock Data: Live Care Reports
let careReports = [
  {
    id: 201,
    bookingId: 101,
    time: '14:05',
    category: 'walk',
    categoryIcon: '🦮',
    title: '산책 시작',
    desc: '초코와 함께 역삼공원 산책을 시작했습니다. 꼬리 흔들며 신나게 출발!'
  },
  {
    id: 202,
    bookingId: 101,
    time: '14:18',
    category: 'stool',
    categoryIcon: '💩',
    title: '배변 완료 (정상변)',
    desc: '공원 잔디밭에서 정상변 1회 시원하게 배변 완료했습니다.'
  },
  {
    id: 203,
    bookingId: 101,
    time: '14:25',
    category: 'meal',
    categoryIcon: '🍖',
    title: '사료 급여 & 음수',
    desc: '요청해주신 사료 50g 깨끗이 다 먹고 물도 100ml 섭취했습니다.'
  }
];

// ==========================================
// Initialization
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  renderHome();
  renderSittersList();
  renderBookingsList();
  renderCareReports();
  loadPetCareCardForm();
  if (window.lucide) lucide.createIcons();
});

// Tab Switcher
window.switchTab = function(tabId) {
  currentTab = tabId;
  document.querySelectorAll('.tab-view').forEach(el => el.classList.add('hidden'));
  const targetView = document.getElementById(`view-${tabId}`);
  if (targetView) targetView.classList.remove('hidden');

  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.remove('active', 'text-emerald-600');
    btn.classList.add('text-slate-400');
  });

  const activeNav = document.getElementById(`nav-${tabId}`);
  if (activeNav) {
    activeNav.classList.add('active', 'text-emerald-600');
    activeNav.classList.remove('text-slate-400');
  }

  if (tabId === 'sitters') {
    renderSittersList();
  } else if (tabId === 'booking') {
    renderBookingsList();
  } else if (tabId === 'reports') {
    renderCareReports();
  }

  if (window.lucide) lucide.createIcons();
};

// ==========================================
// 1. HOME RENDERER
// ==========================================
function renderHome() {
  // 1. Pet Info
  const petNameEl = document.getElementById('home-pet-name');
  const petSubEl = document.getElementById('home-pet-subtext');
  if (petNameEl) petNameEl.textContent = petProfile.name;
  if (petSubEl) petSubEl.textContent = `${petProfile.breed} • ${petProfile.age}세 • ${petProfile.weight}kg`;

  // 2. Upcoming Booking Card
  const upcomingContainer = document.getElementById('home-upcoming-booking-card');
  const activeBooking = bookings.find(b => b.status === 'confirmed' || b.status === 'ongoing');
  if (upcomingContainer) {
    if (activeBooking) {
      upcomingContainer.innerHTML = `
        <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
          <div class="flex items-center gap-2">
            <span class="text-xl">🏡</span>
            <div>
              <h4 class="font-black text-xs text-slate-900">${activeBooking.serviceTitle}</h4>
              <p class="text-[11px] text-emerald-700 font-bold">${activeBooking.sitterName}</p>
            </div>
          </div>
          <span class="text-[10px] bg-emerald-100 text-emerald-800 font-black px-2 py-0.5 rounded-full">${activeBooking.statusLabel}</span>
        </div>
        <div class="flex justify-between items-center text-xs text-slate-600">
          <span class="font-bold">📅 ${activeBooking.date} (${activeBooking.time})</span>
          <button onclick="switchTab('reports')" class="px-2.5 py-1 bg-emerald-600 text-white rounded-xl font-bold text-[11px] hover:bg-emerald-700">라이브 확인</button>
        </div>
      `;
    } else {
      upcomingContainer.innerHTML = `
        <div class="text-center py-3 text-xs text-slate-400">
          <p>예정된 돌봄 일정이 없습니다.</p>
          <button onclick="openFastBookingWizard()" class="mt-2 text-emerald-600 font-bold hover:underline">새 돌봄 예약하기 +</button>
        </div>
      `;
    }
  }

  // 3. Recommended Sitters (Top 2)
  const sittersHomeContainer = document.getElementById('home-sitters-container');
  if (sittersHomeContainer) {
    sittersHomeContainer.innerHTML = SITTERS_DATA.slice(0, 2).map(s => `
      <div onclick="openSitterProfileModal(${s.id})" class="p-3.5 bg-white hover:bg-slate-50 rounded-3xl border border-slate-200/80 shadow-2xs flex items-center justify-between cursor-pointer transition-transform active:scale-98">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center text-2xl shrink-0 shadow-2xs">
            ${s.avatar}
          </div>
          <div>
            <div class="flex items-center gap-1.5">
              <h4 class="font-black text-xs text-slate-900">${s.name}</h4>
              <span class="text-[9px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.2 rounded-full">${s.badge}</span>
            </div>
            <p class="text-[11px] text-slate-500 font-medium">${s.title}</p>
            <p class="text-[10px] text-slate-400 mt-0.5">📍 ${s.location} (${s.distanceKm}km) • ⭐ ${s.rating} (후기 ${s.reviewsCount})</p>
          </div>
        </div>
        <div class="text-right shrink-0">
          <span class="text-xs font-black text-emerald-700 block">${s.pricePerUnit.toLocaleString()}원~</span>
          <span class="text-[10px] text-slate-400">상세보기 &gt;</span>
        </div>
      </div>
    `).join('');
  }

  // 4. Recent Report Summary
  const recentReportContainer = document.getElementById('home-recent-report-card');
  if (recentReportContainer) {
    const latest = careReports[careReports.length - 1];
    if (latest) {
      recentReportContainer.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-bold text-indigo-900">${latest.categoryIcon} ${latest.title}</span>
          <span class="text-[10px] text-indigo-600 font-bold">${latest.time}</span>
        </div>
        <p class="text-xs text-slate-600 leading-snug">${latest.desc}</p>
      `;
    }
  }
}

// ==========================================
// 2. SITTERS LIST & SEARCH
// ==========================================
function renderSittersList() {
  const container = document.getElementById('sitters-list-container');
  if (!container) return;

  const sizeFilter = document.getElementById('sitter-size-filter')?.value || 'all';
  const radiusFilter = document.getElementById('sitter-radius-filter')?.value || 'all';

  let filtered = SITTERS_DATA.filter(s => {
    if (currentSitterFilter !== 'all' && !s.services.includes(currentSitterFilter)) return false;
    if (sizeFilter !== 'all' && !s.sizeSupport.includes(sizeFilter)) return false;
    if (radiusFilter !== 'all' && s.distanceKm > parseFloat(radiusFilter)) return false;
    return true;
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="text-center py-12 text-xs text-slate-400">
        <p class="text-2xl mb-1">🔍</p>
        <p>조건에 맞는 펫시터가 없습니다.</p>
        <button onclick="resetSitterFilters()" class="mt-2 text-emerald-600 font-bold">필터 초기화</button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(s => `
    <div onclick="openSitterProfileModal(${s.id})" class="p-4 bg-white hover:bg-slate-50 rounded-3xl border border-slate-200 shadow-sm cursor-pointer space-y-3 transition-transform active:scale-99">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center text-3xl shrink-0 shadow-2xs">
            ${s.avatar}
          </div>
          <div>
            <div class="flex items-center gap-1.5">
              <h4 class="font-black text-sm text-slate-900">${s.name}</h4>
              <span class="text-[9px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">${s.badge}</span>
            </div>
            <p class="text-xs text-emerald-700 font-bold mt-0.5">${s.title}</p>
            <div class="flex items-center gap-2 text-[11px] text-slate-400 mt-1 font-medium">
              <span>📍 ${s.location} (${s.distanceKm}km)</span>
              <span>⭐ ${s.rating} (${s.reviewsCount})</span>
            </div>
          </div>
        </div>
        <div class="text-right shrink-0">
          <span class="text-sm font-black text-slate-900 block">${s.pricePerUnit.toLocaleString()}원</span>
          <span class="text-[10px] text-slate-400 block">${s.priceUnitStr.split(' ')[0]} 기준</span>
        </div>
      </div>

      <p class="text-xs text-slate-600 line-clamp-2 bg-slate-50 p-2.5 rounded-2xl">
        "${s.intro}"
      </p>

      <div class="flex items-center justify-between pt-1 border-t border-slate-100 text-[11px]">
        <span class="text-slate-500 font-medium">🕒 ${s.availableTimes}</span>
        <span class="text-emerald-600 font-black flex items-center gap-0.5">예약 가능 &gt;</span>
      </div>
    </div>
  `).join('');
}

window.filterSitterService = function(serviceType) {
  currentSitterFilter = serviceType;
  switchTab('sitters');
  document.querySelectorAll('#sitter-service-filter-group button').forEach(btn => {
    btn.classList.remove('active', 'bg-emerald-600', 'text-white');
    btn.classList.add('bg-slate-100', 'text-slate-700');
  });
  renderSittersList();
};

window.setSitterServiceFilter = function(serviceType, btn) {
  currentSitterFilter = serviceType;
  document.querySelectorAll('#sitter-service-filter-group button').forEach(b => {
    b.classList.remove('active', 'bg-emerald-600', 'text-white');
    b.classList.add('bg-slate-100', 'text-slate-700');
  });
  btn.classList.add('active', 'bg-emerald-600', 'text-white');
  btn.classList.remove('bg-slate-100', 'text-slate-700');
  renderSittersList();
};

window.applySitterFilters = function() {
  renderSittersList();
};

window.resetSitterFilters = function() {
  currentSitterFilter = 'all';
  if (document.getElementById('sitter-size-filter')) document.getElementById('sitter-size-filter').value = 'all';
  if (document.getElementById('sitter-radius-filter')) document.getElementById('sitter-radius-filter').value = 'all';
  renderSittersList();
};

window.setSitterViewMode = function(mode) {
  const mapEl = document.getElementById('sitters-map-view');
  const btnList = document.getElementById('btn-view-list');
  const btnMap = document.getElementById('btn-view-map');

  if (mode === 'map') {
    if (mapEl) mapEl.classList.remove('hidden');
    btnMap.classList.add('bg-white', 'text-emerald-700');
    btnMap.classList.remove('text-slate-500');
    btnList.classList.remove('bg-white', 'text-emerald-700');
    btnList.classList.add('text-slate-500');
  } else {
    if (mapEl) mapEl.classList.add('hidden');
    btnList.classList.add('bg-white', 'text-emerald-700');
    btnList.classList.remove('text-slate-500');
    btnMap.classList.remove('bg-white', 'text-emerald-700');
    btnMap.classList.add('text-slate-500');
  }
};

// ==========================================
// 3. SITTER PROFILE MODAL
// ==========================================
window.openSitterProfileModal = function(sitterId) {
  const sitter = SITTERS_DATA.find(s => s.id === sitterId) || SITTERS_DATA[0];
  currentSelectedSitter = sitter;
  bookingDraft.sitterId = sitter.id;

  document.getElementById('modal-sitter-name').textContent = sitter.name;
  document.getElementById('modal-sitter-title').textContent = sitter.title;

  const content = document.getElementById('modal-sitter-content');
  if (content) {
    content.innerHTML = `
      <div class="p-3 bg-emerald-50/70 rounded-2xl border border-emerald-100 space-y-1">
        <span class="text-[10px] font-black text-emerald-800 bg-white px-2 py-0.5 rounded-full">자기소개</span>
        <p class="text-xs text-slate-700 leading-relaxed mt-1">${sitter.intro}</p>
      </div>

      <div class="space-y-1.5">
        <span class="font-black text-xs text-slate-800">📋 주요 경력 & 자격사항</span>
        <p class="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100">${sitter.experience}</p>
      </div>

      <div class="space-y-1.5">
        <span class="font-black text-xs text-slate-800">💰 이용 요금 안내</span>
        <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-100 space-y-1 text-xs">
          <div class="flex justify-between"><span>방문 돌봄 (30분)</span><span class="font-bold">25,000원</span></div>
          <div class="flex justify-between"><span>안심 산책 (60분)</span><span class="font-bold">28,000원</span></div>
          <div class="flex justify-between"><span>종일 데이케어 (8시간)</span><span class="font-bold">60,000원</span></div>
        </div>
      </div>

      <div class="p-2.5 bg-indigo-50/60 rounded-xl border border-indigo-100 text-[11px] text-indigo-900 flex items-center gap-1.5">
        <i data-lucide="shield-check" class="w-4 h-4 text-indigo-600 shrink-0"></i>
        <span>에어커버 최대 500만원 안심 보증이 자동 적용되는 공식 인증 펫시터입니다.</span>
      </div>
    `;
  }

  const modal = document.getElementById('modal-sitter-profile');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    if (window.lucide) lucide.createIcons();
  }
};

window.closeSitterProfileModal = function() {
  const modal = document.getElementById('modal-sitter-profile');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};

window.startBookingWithSitter = function() {
  closeSitterProfileModal();
  openFastBookingWizard(currentSelectedSitter);
};

// ==========================================
// 4. 4-STEP SMART BOOKING WIZARD
// ==========================================
window.openFastBookingWizard = function(sitter = null) {
  bookingWizardStep = 1;
  if (sitter) {
    bookingDraft.sitterId = sitter.id;
  } else if (!bookingDraft.sitterId) {
    bookingDraft.sitterId = SITTERS_DATA[0].id;
  }
  renderBookingWizardStep();
  const modal = document.getElementById('modal-booking-wizard');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};

window.closeBookingWizardModal = function() {
  const modal = document.getElementById('modal-booking-wizard');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};

function renderBookingWizardStep() {
  const badge = document.getElementById('booking-step-badge');
  const content = document.getElementById('booking-wizard-step-content');
  const actions = document.getElementById('booking-wizard-actions');
  const sitter = SITTERS_DATA.find(s => s.id === bookingDraft.sitterId) || SITTERS_DATA[0];

  if (bookingWizardStep === 1) {
    badge.textContent = '1단계: 서비스 & 일정 선택';
    content.innerHTML = `
      <div>
        <label class="font-bold text-slate-700 block mb-1">담당 펫시터</label>
        <div class="p-2.5 bg-emerald-50 rounded-xl font-bold text-emerald-900 flex items-center justify-between">
          <span>${sitter.avatar} ${sitter.name}</span>
          <span class="text-xs text-emerald-700 font-medium">${sitter.title}</span>
        </div>
      </div>

      <div>
        <label class="font-bold text-slate-700 block mb-1">돌봄 서비스 유형</label>
        <div class="grid grid-cols-2 gap-1.5">
          <button type="button" onclick="setBookingDraftService('visit', this)" class="booking-srv-btn active p-2.5 rounded-xl border bg-emerald-600 text-white font-bold text-center">🏠 방문돌봄 (30분)</button>
          <button type="button" onclick="setBookingDraftService('walk', this)" class="booking-srv-btn p-2.5 rounded-xl border bg-slate-50 text-slate-700 font-bold text-center">🦮 안심산책 (60분)</button>
          <button type="button" onclick="setBookingDraftService('daycare', this)" class="booking-srv-btn p-2.5 rounded-xl border bg-slate-50 text-slate-700 font-bold text-center">☀️ 데이케어 (8시간)</button>
          <button type="button" onclick="setBookingDraftService('overnight', this)" class="booking-srv-btn p-2.5 rounded-xl border bg-slate-50 text-slate-700 font-bold text-center">🌙 1박 케어</button>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="font-bold text-slate-700 block mb-1">돌봄 일자</label>
          <input type="date" id="wizard-date" value="2026-09-23" class="w-full p-2.5 rounded-xl border border-slate-200 bg-slate-50 font-bold">
        </div>
        <div>
          <label class="font-bold text-slate-700 block mb-1">시작 시간</label>
          <input type="time" id="wizard-time" value="14:00" class="w-full p-2.5 rounded-xl border border-slate-200 bg-slate-50 font-bold">
        </div>
      </div>
    `;

    actions.innerHTML = `
      <button onclick="closeBookingWizardModal()" class="px-4 py-3 bg-slate-100 text-slate-700 font-bold rounded-2xl text-xs">취소</button>
      <button onclick="goToWizardStep(2)" class="flex-1 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-black rounded-2xl text-xs shadow-md">다음: 케어 카드 확인 (2/3)</button>
    `;
  } else if (bookingWizardStep === 2) {
    badge.textContent = '2단계: 반려견 & Pet Care Card 연동';
    content.innerHTML = `
      <div class="p-3 bg-emerald-50 rounded-2xl border border-emerald-200 space-y-1.5">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🐕</span>
            <div>
              <h4 class="font-black text-xs text-slate-900">${petProfile.name} (${petProfile.breed})</h4>
              <p class="text-[10px] text-slate-500">${petProfile.gender} • ${petProfile.age}세 • ${petProfile.weight}kg</p>
            </div>
          </div>
          <button onclick="openPetCareCardModal()" class="text-[11px] text-emerald-700 font-bold underline">수정</button>
        </div>
      </div>

      <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-200 text-[11px] space-y-1">
        <p><b>🍗 급여:</b> ${petProfile.feedMemo}</p>
        <p><b>💊 알러지/약:</b> ${petProfile.medicine}</p>
        <p><b>🦮 산책 주의:</b> ${petProfile.walkNotes}</p>
        <p><b>🏥 병원:</b> ${petProfile.hospital}</p>
      </div>

      <div>
        <label class="font-bold text-slate-700 block mb-1">펫시터님께 전할 특별 요청사항</label>
        <input type="text" id="wizard-memo" placeholder="예: 현관 비밀번호 및 간식 위치는 채팅으로 공유할게요" class="w-full p-2.5 rounded-xl border border-slate-200 bg-slate-50 font-medium">
      </div>
    `;

    actions.innerHTML = `
      <button onclick="goToWizardStep(1)" class="px-4 py-3 bg-slate-100 text-slate-700 font-bold rounded-2xl text-xs">이전</button>
      <button onclick="goToWizardStep(3)" class="flex-1 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-black rounded-2xl text-xs shadow-md">다음: 전자계약 & 완료 (3/3)</button>
    `;
  } else if (bookingWizardStep === 3) {
    badge.textContent = '3단계: 안심 전자계약 & 예약 확정';
    content.innerHTML = `
      <div class="p-3.5 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-2xl border border-emerald-200 space-y-2">
        <div class="flex justify-between items-center font-black">
          <span class="text-emerald-900 text-xs">🛡️ 디지털 안심 돌봄 계약 체결</span>
          <span class="text-[10px] bg-emerald-600 text-white px-2 py-0.5 rounded-full">에어커버 500만원</span>
        </div>
        <p class="text-[11px] text-slate-600 leading-relaxed">
          본 예약은 전자상거래법 제20조 제2항에 따른 통신판매중개 규정 및 멍당근/펫케어메이트 안심 돌봄 표준 약관에 따라 안전하게 체결됩니다.
        </p>
      </div>

      <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
        <div class="flex justify-between font-bold"><span>예약 일시:</span><span>${document.getElementById('wizard-date')?.value || '2026-09-23'} 14:00</span></div>
        <div class="flex justify-between font-bold"><span>돌봄 대상:</span><span>${petProfile.name} (말티즈)</span></div>
        <div class="flex justify-between font-bold"><span>결제 예정 금액:</span><span class="text-emerald-700 font-black">25,000원 (현장/안심정산)</span></div>
      </div>
    `;

    actions.innerHTML = `
      <button onclick="goToWizardStep(2)" class="px-4 py-3 bg-slate-100 text-slate-700 font-bold rounded-2xl text-xs">이전</button>
      <button onclick="confirmAndFinishBooking()" class="flex-1 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-black rounded-2xl text-xs shadow-lg shadow-emerald-500/30">
        전자서명 & 예약 완료하기 ✨
      </button>
    `;
  }
}

window.goToWizardStep = function(step) {
  bookingWizardStep = step;
  renderBookingWizardStep();
};

window.setBookingDraftService = function(srv, btn) {
  bookingDraft.service = srv;
  document.querySelectorAll('.booking-srv-btn').forEach(b => {
    b.classList.remove('active', 'bg-emerald-600', 'text-white');
    b.classList.add('bg-slate-50', 'text-slate-700');
  });
  btn.classList.add('active', 'bg-emerald-600', 'text-white');
  btn.classList.remove('bg-slate-50', 'text-slate-700');
};

window.confirmAndFinishBooking = function() {
  const newBooking = {
    id: Date.now(),
    sitterId: bookingDraft.sitterId,
    sitterName: SITTERS_DATA.find(s => s.id === bookingDraft.sitterId)?.name || '이지은 펫시터',
    serviceTitle: '🏠 방문 돌봄 (30분)',
    date: '2026-09-23',
    time: '14:00 ~ 14:30',
    petName: petProfile.name,
    price: 25000,
    status: 'confirmed',
    statusLabel: '예약 확정',
    memo: '안심 케어 카드 전달 완료'
  };

  bookings.unshift(newBooking);
  closeBookingWizardModal();
  alert('🎉 안심 돌봄 예약이 성공적으로 완료되었습니다!\n펫시터에게 케어 카드가 전송되었습니다.');
  renderHome();
  renderBookingsList();
  switchTab('booking');
};

// ==========================================
// 5. BOOKINGS LIST
// ==========================================
function renderBookingsList() {
  const container = document.getElementById('bookings-list-container');
  if (!container) return;

  const filtered = bookings.filter(b => {
    if (currentBookingFilter === 'active') return b.status === 'confirmed' || b.status === 'ongoing';
    return b.status === 'completed';
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="text-center py-12 text-xs text-slate-400">
        <p class="text-2xl mb-1">📅</p>
        <p>해당하는 돌봄 내역이 없습니다.</p>
        <button onclick="openFastBookingWizard()" class="mt-2 text-emerald-600 font-bold">새 돌봄 예약하기 +</button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(b => `
    <div class="p-4 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-3">
      <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
        <div class="flex items-center gap-2">
          <span class="text-2xl">🏡</span>
          <div>
            <h4 class="font-black text-xs text-slate-900">${b.serviceTitle}</h4>
            <p class="text-[11px] text-emerald-700 font-bold">${b.sitterName}</p>
          </div>
        </div>
        <span class="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">${b.statusLabel}</span>
      </div>

      <div class="text-xs text-slate-600 space-y-1">
        <div class="flex justify-between"><span>돌봄 일시:</span><span class="font-bold text-slate-800">${b.date} (${b.time})</span></div>
        <div class="flex justify-between"><span>돌봄 대상:</span><span class="font-bold text-slate-800">${b.petName}</span></div>
        <div class="flex justify-between"><span>결제 금액:</span><span class="font-black text-emerald-700">${b.price.toLocaleString()}원</span></div>
      </div>

      <div class="pt-1 flex gap-2">
        <button onclick="switchTab('reports')" class="flex-1 py-2.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-bold rounded-xl text-xs">
          실시간 리포트 보기
        </button>
        <button onclick="openPetCareCardModal()" class="px-3 py-2.5 bg-slate-100 text-slate-700 font-bold rounded-xl text-xs">
          케어카드
        </button>
      </div>
    </div>
  `).join('');
}

window.switchBookingFilter = function(filterType) {
  currentBookingFilter = filterType;
  const btnActive = document.getElementById('btn-booking-tab-active');
  const btnPast = document.getElementById('btn-booking-tab-past');
  if (filterType === 'active') {
    btnActive.className = 'flex-1 py-1.5 rounded-xl bg-white text-emerald-700 shadow-2xs text-center transition-all';
    btnPast.className = 'flex-1 py-1.5 rounded-xl text-slate-500 hover:text-slate-800 text-center transition-all';
  } else {
    btnPast.className = 'flex-1 py-1.5 rounded-xl bg-white text-emerald-700 shadow-2xs text-center transition-all';
    btnActive.className = 'flex-1 py-1.5 rounded-xl text-slate-500 hover:text-slate-800 text-center transition-all';
  }
  renderBookingsList();
};

// ==========================================
// 6. CARE REPORTS
// ==========================================
function renderCareReports() {
  const activeContainer = document.getElementById('live-report-active-container');
  const pastContainer = document.getElementById('past-reports-archive-list');

  if (activeContainer) {
    activeContainer.innerHTML = `
      <div class="p-4 bg-gradient-to-r from-emerald-50 via-teal-50 to-indigo-50 rounded-3xl border border-emerald-200 shadow-sm space-y-3">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-1.5">
            <span class="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="font-black text-xs text-emerald-950">오늘의 라이브 돌봄 타임라인</span>
          </div>
          <span class="text-[10px] bg-emerald-600 text-white px-2 py-0.5 rounded-full font-bold">진행중</span>
        </div>

        <div class="space-y-2 relative pl-4 border-l-2 border-emerald-300">
          ${careReports.map(r => `
            <div class="relative space-y-0.5">
              <div class="absolute -left-[21px] top-0.5 w-3.5 h-3.5 rounded-full bg-emerald-600 border-2 border-white"></div>
              <div class="flex justify-between text-[11px]">
                <span class="font-black text-slate-800">${r.categoryIcon} ${r.title}</span>
                <span class="text-slate-400 font-bold">${r.time}</span>
              </div>
              <p class="text-xs text-slate-600 leading-snug">${r.desc}</p>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  if (pastContainer) {
    pastContainer.innerHTML = `
      <div class="p-3.5 bg-white rounded-2xl border border-slate-200 text-xs flex justify-between items-center shadow-2xs">
        <div>
          <span class="font-black text-slate-900 block">2026-09-18 안심 산책 리포트 (박준혁 펫시터)</span>
          <span class="text-[10px] text-slate-400">산책 60분 • 배변 1회 • 사진 4장 포함</span>
        </div>
        <button onclick="alert('📸 사진 4장이 포함된 지난 리포트입니다.')" class="px-2.5 py-1 bg-slate-100 text-slate-700 font-bold rounded-xl text-[11px]">보기</button>
      </div>
    `;
  }
}

window.openCareReportWriteModal = function() {
  const modal = document.getElementById('modal-care-report-write');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};

window.closeCareReportWriteModal = function() {
  const modal = document.getElementById('modal-care-report-write');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};

let currentReportCategory = 'walk';
window.selectReportCategory = function(cat, btn) {
  currentReportCategory = cat;
  document.querySelectorAll('.report-cat-btn').forEach(b => {
    b.classList.remove('active', 'bg-indigo-600', 'text-white');
    b.classList.add('bg-slate-50', 'text-slate-700');
  });
  btn.classList.add('active', 'bg-indigo-600', 'text-white');
  btn.classList.remove('bg-slate-50', 'text-slate-700');
};

window.saveCareReportEntry = function(e) {
  e.preventDefault();
  const memo = document.getElementById('report-memo-input').value.trim();
  if (!memo) {
    alert('내용을 입력해주세요.');
    return;
  }

  const icons = { walk: '🦮', meal: '🍖', stool: '💩', photo: '📷' };
  const titles = { walk: '산책 일지', meal: '식사/간식 급여', stool: '배변 상태', photo: '현장 사진' };

  careReports.push({
    id: Date.now(),
    bookingId: 101,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    category: currentReportCategory,
    categoryIcon: icons[currentReportCategory] || '📝',
    title: titles[currentReportCategory] || '돌봄 기록',
    desc: memo
  });

  closeCareReportWriteModal();
  document.getElementById('report-memo-input').value = '';
  alert('📢 실시간 돌봄 리포트가 보호자에게 전송되었습니다!');
  renderHome();
  renderCareReports();
};

// ==========================================
// 7. PET CARE CARD MODAL LOGIC
// ==========================================
function loadPetCareCardForm() {
  if (document.getElementById('pcc-name')) document.getElementById('pcc-name').value = petProfile.name;
  if (document.getElementById('pcc-breed')) document.getElementById('pcc-breed').value = petProfile.breed;
  if (document.getElementById('pcc-age')) document.getElementById('pcc-age').value = petProfile.age;
  if (document.getElementById('pcc-gender')) document.getElementById('pcc-gender').value = petProfile.gender;
  if (document.getElementById('pcc-weight')) document.getElementById('pcc-weight').value = petProfile.weight;
  if (document.getElementById('pcc-feed-memo')) document.getElementById('pcc-feed-memo').value = petProfile.feedMemo;
  if (document.getElementById('pcc-medicine')) document.getElementById('pcc-medicine').value = petProfile.medicine;
  if (document.getElementById('pcc-walk-notes')) document.getElementById('pcc-walk-notes').value = petProfile.walkNotes;
  if (document.getElementById('pcc-hospital')) document.getElementById('pcc-hospital').value = petProfile.hospital;
  if (document.getElementById('pcc-emergency')) document.getElementById('pcc-emergency').value = petProfile.emergency;
}

window.openPetCareCardModal = function() {
  loadPetCareCardForm();
  const modal = document.getElementById('modal-pet-care-card');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};

window.closePetCareCardModal = function() {
  const modal = document.getElementById('modal-pet-care-card');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};

window.savePetCareCard = function(e) {
  e.preventDefault();
  petProfile.name = document.getElementById('pcc-name').value.trim();
  petProfile.breed = document.getElementById('pcc-breed').value.trim();
  petProfile.age = parseInt(document.getElementById('pcc-age').value) || 3;
  petProfile.gender = document.getElementById('pcc-gender').value;
  petProfile.weight = parseFloat(document.getElementById('pcc-weight').value) || 3.4;
  petProfile.feedMemo = document.getElementById('pcc-feed-memo').value.trim();
  petProfile.medicine = document.getElementById('pcc-medicine').value.trim();
  petProfile.walkNotes = document.getElementById('pcc-walk-notes').value.trim();
  petProfile.hospital = document.getElementById('pcc-hospital').value.trim();
  petProfile.emergency = document.getElementById('pcc-emergency').value.trim();

  closePetCareCardModal();
  alert('✨ 내 아이 안심 케어 카드가 저장되었습니다!');
  renderHome();
};

// ==========================================
// 8. AI SCANNER & MBTI & DOCTOR CHART MODALS
// ==========================================
window.openAIScannerModal = function() {
  const modal = document.getElementById('modal-ai-scanner');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};
window.closeAIScannerModal = function() {
  const modal = document.getElementById('modal-ai-scanner');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};
window.triggerAIScan = function() {
  const box = document.getElementById('ai-scan-result-box');
  if (box) {
    box.classList.remove('hidden');
    alert('📸 Gemini 비전 AI가 사진을 1초 만에 분석하였습니다!');
  }
};

window.openMBTIModal = function() {
  const modal = document.getElementById('modal-mbti-compat');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};
window.closeMBTIModal = function() {
  const modal = document.getElementById('modal-mbti-compat');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};

window.openDoctorChartModal = function() {
  const modal = document.getElementById('modal-doctor-chart');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};
window.closeDoctorChartModal = function() {
  const modal = document.getElementById('modal-doctor-chart');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};

window.selectHealthCheck = function(btn, type, val) {
  btn.parentElement.querySelectorAll('button').forEach(b => {
    b.classList.remove('bg-emerald-600', 'text-white', 'font-bold');
  });
  btn.classList.add('bg-emerald-600', 'text-white', 'font-bold');
};

window.saveHealthLog = function() {
  alert('📋 오늘의 건강 기록이 저장되었습니다!');
  closeDoctorChartModal();
};

window.exportChartPDF = function() {
  alert('📄 [PDF 차트 출력]\n오늘의 닥터 건강 차트가 PDF로 출력되었습니다.');
};

// ==========================================
// 9. TERMS & AIRCOVER SYSTEM
// ==========================================
const TERMS_DATA = {
  terms: {
    icon: '⚖️',
    title: '서비스 이용약관 & 통신판매중개 면책조항',
    html: `
      <div class="space-y-2">
        <p class="font-bold text-emerald-900">📌 전자상거래법 제20조 제2항 준용 고지</p>
        <p>펫케어 메이트는 회원 간의 1:1 펫시터 매칭 플랫폼을 제공하는 통신판매중개자이며, 당사자 간의 돌봄 행위에 대하여 일체의 책임을 부담하지 아니합니다.</p>
      </div>
    `
  },
  privacy: {
    icon: '🔒',
    title: '개인정보 처리방침 & 위치기반서비스',
    html: `
      <div class="space-y-2">
        <p class="font-bold text-emerald-900">🛡️ 실시간 위치 비저장 원칙</p>
        <p>동네 반경 검색은 단말기 내에서만 일시 계산되며 실시간 위치 좌표는 외부 서버에 보관되지 않습니다.</p>
      </div>
    `
  },
  aircover: {
    icon: '🛡️',
    title: '에어커버 최대 500만원 안심 보증 규정',
    html: `
      <div class="space-y-2">
        <p class="font-bold text-emerald-900">🏥 돌봄 중 사고 병원비 실비 지원</p>
        <p>전자계약서가 체결된 정식 매칭 중 발생한 급성 상해/사고에 대해 사고당 최대 500만원 실손 지원합니다. (기저질환/고의 제외)</p>
      </div>
    `
  }
};

window.openTermsModal = function(type) {
  const data = TERMS_DATA[type] || TERMS_DATA.terms;
  const modal = document.getElementById('modal-terms');
  document.getElementById('terms-modal-icon').textContent = data.icon;
  document.getElementById('terms-modal-title').textContent = data.title;
  document.getElementById('terms-modal-body').innerHTML = data.html;

  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};

window.closeTermsModal = function() {
  const modal = document.getElementById('modal-terms');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};

// ==========================================
// 10. AUTH MODAL
// ==========================================
window.openAuthModal = function() {
  const modal = document.getElementById('modal-auth');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};

window.closeAuthModal = function() {
  const modal = document.getElementById('modal-auth');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};

window.loginWithKakao = function() {
  alert('💬 카카오 계정으로 간편 로그인이 완료되었습니다!');
  closeAuthModal();
};

window.loginWithGoogle = function() {
  alert('🌐 Google 계정으로 로그인이 완료되었습니다!');
  closeAuthModal();
};
