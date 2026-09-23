// ==========================================
// 🩺 [DAILY PET HEALTH APP - JAVASCRIPT CORE]
// 펫닥터 데일리 - 반려견 건강기록 & AI 상태 분석
// ==========================================

// Global State
let currentTab = 'home';
let currentSelectedMeal = '정상';
let currentSelectedWater = '적당함';
let currentSelectedStool = '정상변';

// 1. Mock Data: Pet Profile
let petProfile = {
  name: '초코',
  breed: '말티즈',
  age: 3,
  gender: '남아 (중성화 O)',
  weight: 3.4,
  conditionNotes: '슬개골 탈구 1기 관리중'
};

// 2. Mock Data: Daily Health Timeline Events
let timelineEvents = [
  {
    id: 1,
    date: '2026-09-21',
    time: '09:30',
    type: 'check',
    typeIcon: '🩺',
    title: '오늘의 10초 건강 기록',
    meal: '정상 🍖',
    stool: '정상변 💩',
    walkMin: 35,
    mood: '신남 😊',
    memo: '컨디션 매우 양호, 관절 영양제 1알 복용 완료'
  },
  {
    id: 2,
    date: '2026-09-20',
    time: '18:40',
    type: 'ai-voice',
    typeIcon: '🎙️',
    title: 'AI 음성 분석',
    meal: '-',
    stool: '-',
    walkMin: 40,
    mood: '흥분',
    memo: '저녁 산책 직전 신난 요구성 짖음 패턴 (흥분 지수 82%)'
  },
  {
    id: 3,
    date: '2026-09-18',
    time: '14:20',
    type: 'vaccine',
    typeIcon: '💉',
    title: '심장사상충 예방약 복용',
    meal: '정상',
    stool: '정상변',
    walkMin: 30,
    mood: '보통',
    memo: '하트가드 1정 급여 완료'
  }
];

// 3. Mock Data: Schedules & D-Days
let schedules = [
  {
    id: 1,
    type: 'vaccine',
    typeIcon: '💉',
    title: '광견병 예방접종',
    date: '2026-10-03',
    ddayStr: 'D-12',
    hospital: '역삼 24시 동물병원'
  },
  {
    id: 2,
    type: 'heartworm',
    typeIcon: '💊',
    title: '심장사상충 정기 투약',
    date: '2026-10-18',
    ddayStr: 'D-27',
    hospital: '자가 투약'
  }
];

// 4. Mock Data: Animal Hospitals Database
const HOSPITALS_DATA = [
  {
    id: 1,
    name: '역삼 24시 동물의료센터',
    category: '24시 야간응급 • 내과/외과',
    address: '서울 강남구 테헤란로 123',
    distanceKm: 0.4,
    phone: '02-1234-5678',
    isOpen: true,
    is24h: true,
    isSurgery: true,
    hours: '24시간 연중무휴 (야간응급실 운영)'
  },
  {
    id: 2,
    name: '강남 사랑 동물병원',
    category: '정형외과 • 슬개골 전문',
    address: '서울 강남구 역삼로 45',
    distanceKm: 0.9,
    phone: '02-9876-5432',
    isOpen: true,
    is24h: false,
    isSurgery: true,
    hours: '월~토 09:30 ~ 20:00 (일요일 휴진)'
  },
  {
    id: 3,
    name: '도곡 24시 웰니스 동물메디컬',
    category: '24시 응급 • 노령견 케어',
    address: '서울 강남구 남부순환로 789',
    distanceKm: 1.6,
    phone: '02-5555-7777',
    isOpen: true,
    is24h: true,
    isSurgery: false,
    hours: '24시간 365일 진료'
  }
];

// ==========================================
// Initialization
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  renderHome();
  renderTimeline();
  renderHospitalsList();
  if (window.lucide) lucide.createIcons();
});

// Tab Switcher
window.switchTab = function(tabId) {
  currentTab = tabId;
  document.querySelectorAll('.tab-view').forEach(el => el.classList.add('hidden'));
  const targetView = document.getElementById(`view-${tabId}`);
  if (targetView) targetView.classList.remove('hidden');

  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.remove('active', 'text-teal-600');
    btn.classList.add('text-slate-400');
  });

  const activeNav = document.getElementById(`nav-${tabId}`);
  if (activeNav) {
    activeNav.classList.add('active', 'text-teal-600');
    activeNav.classList.remove('text-slate-400');
  }

  if (tabId === 'timeline') renderTimeline();
  if (tabId === 'hospitals') renderHospitalsList();

  if (window.lucide) lucide.createIcons();
};

// ==========================================
// 1. HOME RENDERER
// ==========================================
function renderHome() {
  document.getElementById('home-pet-name').textContent = petProfile.name;
  document.getElementById('hero-pet-name').textContent = petProfile.name;
  document.getElementById('home-pet-subtext').textContent = `${petProfile.breed} • ${petProfile.age}세 • ${petProfile.weight}kg`;

  // Quick Hospital in Home
  const hospBox = document.getElementById('home-quick-hospital-box');
  if (hospBox) {
    hospBox.innerHTML = HOSPITALS_DATA.slice(0, 2).map(h => `
      <div class="p-3 bg-slate-50 hover:bg-teal-50/50 rounded-2xl border border-slate-100 flex items-center justify-between text-xs">
        <div>
          <div class="flex items-center gap-1.5">
            <span class="font-black text-slate-900">${h.name}</span>
            <span class="text-[9px] bg-teal-100 text-teal-800 font-bold px-1.5 py-0.2 rounded-full">${h.is24h ? '24시 응급' : '영업중'}</span>
          </div>
          <p class="text-[10px] text-slate-400 mt-0.5">📍 ${h.distanceKm}km • ${h.phone}</p>
        </div>
        <a href="tel:${h.phone}" class="px-2.5 py-1.5 bg-teal-600 text-white font-bold rounded-xl text-[11px] shadow-2xs">전화연결</a>
      </div>
    `).join('');
  }
}

// ==========================================
// 2. 10-SECOND DAILY V-CHECK MODAL
// ==========================================
window.openDailyCheckModal = function() {
  const modal = document.getElementById('modal-daily-check');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    if (window.lucide) lucide.createIcons();
  }
};

window.closeDailyCheckModal = function() {
  const modal = document.getElementById('modal-daily-check');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};

window.selectDailyOption = function(type, val, btn) {
  if (type === 'meal') currentSelectedMeal = val;
  if (type === 'water') currentSelectedWater = val;
  if (type === 'stool') currentSelectedStool = val;

  btn.parentElement.querySelectorAll('button').forEach(b => {
    b.classList.remove('active', 'bg-teal-600', 'text-white');
  });
  btn.classList.add('active', 'bg-teal-600', 'text-white');
};

window.saveDailyCheck = function(e) {
  e.preventDefault();
  const walkMin = parseInt(document.getElementById('dc-walk-min')?.value) || 30;
  const mood = document.getElementById('dc-mood')?.value || '신남 😊';
  const memo = document.getElementById('dc-memo')?.value.trim() || '특이사항 없음 (양호)';

  // Update quick pills in Home
  document.getElementById('quick-status-meal').textContent = `${currentSelectedMeal} 🍖`;
  document.getElementById('quick-status-stool').textContent = `${currentSelectedStool} 💩`;
  document.getElementById('quick-status-walk').textContent = `${walkMin}분 🦮`;
  document.getElementById('quick-status-mood').textContent = `${mood.split(' ')[0]}`;

  timelineEvents.unshift({
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    type: 'check',
    typeIcon: '🩺',
    title: '오늘의 10초 건강 기록',
    meal: currentSelectedMeal,
    stool: currentSelectedStool,
    walkMin: walkMin,
    mood: mood,
    memo: memo
  });

  closeDailyCheckModal();
  alert('✨ 10초 데일리 건강 기록이 안전하게 저장되었습니다!');
  renderHome();
  renderTimeline();
};

// ==========================================
// 3. HEALTH TIMELINE RENDERER
// ==========================================
function renderTimeline() {
  const container = document.getElementById('timeline-events-container');
  if (!container) return;

  container.innerHTML = `
    <div class="space-y-3 relative pl-4 border-l-2 border-teal-300">
      ${timelineEvents.map(ev => `
        <div class="relative space-y-1">
          <div class="absolute -left-[21px] top-1 w-3.5 h-3.5 rounded-full bg-teal-600 border-2 border-white"></div>
          <div class="p-4 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-2">
            <div class="flex justify-between items-center border-b border-slate-100 pb-2">
              <div class="flex items-center gap-1.5 font-black text-xs text-slate-900">
                <span>${ev.typeIcon}</span>
                <span>${ev.title}</span>
              </div>
              <span class="text-[10px] text-slate-400 font-bold">${ev.date} ${ev.time}</span>
            </div>

            <div class="grid grid-cols-3 gap-1 text-[11px] text-slate-600 bg-slate-50 p-2 rounded-xl">
              <span>식사: <b>${ev.meal}</b></span>
              <span>배변: <b>${ev.stool}</b></span>
              <span>산책: <b>${ev.walkMin}분</b></span>
            </div>

            <p class="text-xs text-slate-700 leading-snug">${ev.memo}</p>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

// ==========================================
// 4. ANIMAL HOSPITALS LOCATOR
// ==========================================
let currentHospFilter = 'all';
function renderHospitalsList() {
  const container = document.getElementById('hospitals-list-container');
  if (!container) return;

  let filtered = HOSPITALS_DATA.filter(h => {
    if (currentHospFilter === '24h') return h.is24h;
    if (currentHospFilter === 'open') return h.isOpen;
    if (currentHospFilter === 'surgery') return h.isSurgery;
    return true;
  });

  container.innerHTML = filtered.map(h => `
    <div class="p-4 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-2.5">
      <div class="flex justify-between items-start">
        <div>
          <div class="flex items-center gap-1.5">
            <h4 class="font-black text-sm text-slate-900">${h.name}</h4>
            <span class="text-[9px] ${h.is24h ? 'bg-rose-100 text-rose-800' : 'bg-teal-100 text-teal-800'} font-black px-1.5 py-0.2 rounded-full">${h.is24h ? '24시 응급' : '영업중'}</span>
          </div>
          <p class="text-xs text-teal-700 font-bold mt-0.5">${h.category}</p>
          <p class="text-[11px] text-slate-400 mt-0.5">📍 ${h.address} (${h.distanceKm}km)</p>
        </div>
      </div>

      <p class="text-[11px] text-slate-500 bg-slate-50 p-2 rounded-xl">
        🕒 ${h.hours}
      </p>

      <div class="flex gap-2 pt-1 border-t border-slate-100 text-xs">
        <a href="tel:${h.phone}" class="flex-1 py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-black rounded-xl text-center shadow-xs">
          📞 전화 걸기 (${h.phone})
        </a>
        <button onclick="alert('🗺️ 카카오맵 길찾기로 연결됩니다.')" class="px-4 py-2.5 bg-slate-100 text-slate-700 font-bold rounded-xl">
          길찾기
        </button>
      </div>
    </div>
  `).join('');
}

window.filterHospitals = function(filterType, btn) {
  currentHospFilter = filterType;
  document.querySelectorAll('#hospital-filter-group button').forEach(b => {
    b.classList.remove('active', 'bg-teal-600', 'text-white');
    b.classList.add('bg-slate-100', 'text-slate-700');
  });
  btn.classList.add('active', 'bg-teal-600', 'text-white');
  btn.classList.remove('bg-slate-100', 'text-slate-700');
  renderHospitalsList();
};

window.toggleHospitalMap = function() {
  const mapEl = document.getElementById('hospital-map-container');
  if (mapEl) {
    mapEl.classList.toggle('hidden');
  }
};

// ==========================================
// 5. SCHEDULE & D-DAY MODAL
// ==========================================
window.openScheduleAddModal = function() {
  const modal = document.getElementById('modal-schedule-add');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};
window.closeScheduleAddModal = function() {
  const modal = document.getElementById('modal-schedule-add');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};
window.saveSchedule = function(e) {
  e.preventDefault();
  const title = document.getElementById('sch-title').value.trim();
  const date = document.getElementById('sch-date').value;
  alert(`💉 [${title}] 일정이 등록되었습니다! D-Day 알림이 설정됩니다.`);
  closeScheduleAddModal();
};

// ==========================================
// 6. AI VOICE & PHOTO SCAN MODALS
// ==========================================
window.openVoiceRecorderModal = function() {
  const modal = document.getElementById('modal-voice-recorder');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};
window.closeVoiceRecorderModal = function() {
  const modal = document.getElementById('modal-voice-recorder');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};
window.startVoiceRecordingSim = function() {
  const status = document.getElementById('voice-record-status');
  status.textContent = '🎙️ 소리 녹음 중... (3초 남음)';
  setTimeout(() => {
    status.textContent = '✨ AI 주파수 분석 완료!';
    document.getElementById('voice-record-result-box').classList.remove('hidden');
  }, 1500);
};
window.saveAIVoiceToTimeline = function() {
  timelineEvents.unshift({
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    type: 'ai-voice',
    typeIcon: '🎙️',
    title: 'AI 음성 주파수 분석',
    meal: '-',
    stool: '-',
    walkMin: 0,
    mood: '흥분/요구',
    memo: '놀아달라는 요구성 짖음 패턴 (흥분 지수 82%)'
  });
  closeVoiceRecorderModal();
  alert('타임라인에 저장되었습니다.');
  renderTimeline();
};

window.openPhotoScannerModal = function() {
  const modal = document.getElementById('modal-photo-scanner');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};
window.closePhotoScannerModal = function() {
  const modal = document.getElementById('modal-photo-scanner');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};
window.simulatePhotoScan = function() {
  document.getElementById('photo-scan-result-box').classList.remove('hidden');
};
window.saveAIPhotoToTimeline = function() {
  timelineEvents.unshift({
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    type: 'ai-photo',
    typeIcon: '📸',
    title: 'Gemini AI 비전 사진 분석',
    meal: '-',
    stool: '-',
    walkMin: 0,
    mood: '양호',
    memo: '피부 경미 발적 소견 (습도 조절 및 저자극 샴푸 관리 권장)'
  });
  closePhotoScannerModal();
  alert('타임라인에 저장되었습니다.');
  renderTimeline();
};

// ==========================================
// 7. 30-DAY MONTHLY REPORT
// ==========================================
window.openMonthlyReportModal = function() {
  const modal = document.getElementById('modal-monthly-report');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
};
window.closeMonthlyReportModal = function() {
  const modal = document.getElementById('modal-monthly-report');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};
window.exportMonthlyReportPDF = function() {
  alert('📄 [PDF 출력 완료]\n최근 30일 건강 종합 리포트가 PDF로 다운로드되었습니다.');
};

// ==========================================
// 8. TERMS MODAL
// ==========================================
window.openTermsModal = function(type) {
  const modal = document.getElementById('modal-terms');
  const title = document.getElementById('terms-modal-title');
  const body = document.getElementById('terms-modal-body');
  if (type === 'terms') {
    title.textContent = '서비스 이용약관 & 의료법 면책 고지';
    body.innerHTML = `
      <p class="font-bold text-teal-900">📌 의료법 및 수의사법 준수 고지</p>
      <p>본 앱에서 제공하는 AI 상태 분석, 일일 기록 및 30일 건강 리포트는 수의사의 의학적 진단 및 처방을 대신하지 않습니다. 이상 징후 발생 시 동물병원 진료를 권장합니다.</p>
    `;
  } else {
    title.textContent = '개인정보 처리방침 & 위치기반서비스';
    body.innerHTML = `
      <p class="font-bold text-teal-900">🛡️ 실시간 위치 비저장 원칙</p>
      <p>가까운 동물병원 검색은 사용자 단말기 내에서 거리 계산용으로만 일시 활용되며 서버에 영구 보관되지 않습니다.</p>
    `;
  }
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

window.openPetProfileModal = function() {
  alert('🐕 [초코 프로필]\n말티즈 • 3세 • 남아 (중성화 O)\n체중: 3.4kg\n특이사항: 슬개골 탈구 1기 관리중');
};
