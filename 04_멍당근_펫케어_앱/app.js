// MungDanggeun Ultimate 100% Free Production Engine

// ================= 1. Global State =================
let currentUser = null;
let currentPet = { name: '초코', breed: '말티즈', age: '3세', weight: '3.4kg' };
let currentAppMode = 'owner'; // 'owner' | 'sitter'
let currentSitterFeedTab = 'sitters'; // 'sitters' | 'requests'
let currentMarketFilter = 'all';
let currentMarketRadius = 1;
let currentSelectedTradeMode = 'free';
let isMungVoiceAlarmEnabled = true;
let selectedVoiceId = 1;
let tempSelectedVoiceId = 1;
let currentPreviewAudio = null;
let bannerDismissTimer = null;
let latestAlarmItem = null;
let tempReqCareTags = ['단독 산책 2회', '정시 투약/안약', '30분 포토리포트'];
let tempSitterEnvTags = ['24시 상주', '단독 케어', '슬개골 안심매트'];
let currentTargetRequestId = null;
let currentContractContext = null;

// Health Logs State
let healthLogs = [
  { id: 1, date: '2026-09-19', appetite: '정상', stool: '정상변', symptoms: [], memo: '아침 사료 완식. 산책 35분 완료.' },
  { id: 2, date: '2026-09-18', appetite: '약간감소', stool: '묽은변', symptoms: ['가려움/긁음'], memo: '발바닥을 조금 핥음.' }
];
let currentSelectedAppetite = '정상';
let currentSelectedStool = '정상변';
let currentSelectedSymptoms = [];

// 10-Voice Options Definition
const MUNG_VOICE_OPTIONS = [
  { id: 1, title: '1번. 기본 앙증 애교 ("멍 당그은~?")', tag: '추천 No.1', desc: '4번 스타일의 가장 맑고 앙증맞은 대표 음성' },
  { id: 2, title: '2번. 까르르 명랑 톤 ("멍! 당그은~?")', tag: '경쾌 발랄', desc: '아이의 웃음기가 섞인 높은 텐션의 목소리' },
  { id: 3, title: '3번. 콩닥 설렘 톤 ("멍... 당그은?!")', tag: '호기심 톡톡', desc: '선물을 발견하고 깜짝 놀란 귀여운 억양' },
  { id: 4, title: '4번. 오리지널 러블리 ("멍 당그은~")', tag: '원조 4번', desc: '사용자 만족도 최고 오리지널 5세 목소리' },
  { id: 5, title: '5번. 똑똑이 요정 톤 ("멍! 당근이야!")', tag: '똑부러짐', desc: '또박또박 나눔을 알려주는 깜찍한 톤' },
  { id: 6, title: '6번. 댕댕 애교 톤 ("멍~ 당그은~")', tag: '초특급 애교', desc: '꼬리를 살랑살랑 흔드는 듯한 달콤한 콧소리' },
  { id: 7, title: '7번. 속닥 비밀 톤 ("멍... 당근!")', tag: '속닥속닥', desc: '우리 둘만의 비밀 나눔인 듯 귓속말 느낌' },
  { id: 8, title: '8번. 쫑긋 반가움 톤 ("멍?! 당그은~")', tag: '반가움 가득', desc: '동네 친구를 만났을 때 쫑긋 세운 목소리' },
  { id: 9, title: '9번. 씩씩 댕댕 톤 ("멍멍! 당근!")', tag: '활기 100%', desc: '공놀이 직전의 씩씩하고 활기찬 톤' },
  { id: 10, title: '10번. 스윗 굿모닝 톤 ("멍~ 좋은당근~")', tag: '포근 따뜻', desc: '포근하고 부드럽게 울리는 아기 음성' }
];

// Market Initial Items
const DEFAULT_MARKET_ITEMS = [
  {
    id: 1,
    title: '3.5kg 소형견 겨울 기모 패딩 나눔해요 🐾',
    type: 'free',
    price: 0,
    category: 'cloth',
    seller: '역삼 래미안 뽀삐맘 (3.4kg)',
    distance: '250m (도보 3분)',
    distanceKm: 0.25,
    temp: '99.2℃',
    desc: '작년에 사서 2번 입히고 깨끗하게 보관 중입니다. 3kg~4kg 아이들에게 예쁘게 맞습니다.',
    img: 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=500&auto=format&fit=crop&q=80'
  },
  {
    id: 2,
    title: '로얄캐닌 사료 소분 1kg 기호성 테스트용 나눔 🍗',
    type: 'free',
    price: 0,
    category: 'food',
    seller: '역삼 센트럴 몽이네',
    distance: '450m (도보 6분)',
    distanceKm: 0.45,
    temp: '98.8℃',
    desc: '대용량 구매 후 소분 밀봉해둔 새 제품입니다. 입맛 까다로운 아이 테스트용으로 가져가세요!',
    img: 'https://images.unsplash.com/photo-1568640347023-a616a30bc3bd?w=500&auto=format&fit=crop&q=80'
  },
  {
    id: 3,
    title: '원목 2구 식기 & 노즈워크 장난감 🧸',
    type: 'sale',
    price: 15000,
    category: 'gear',
    seller: '도곡동 콩이아빠',
    distance: '1.2km (차량 3분)',
    distanceKm: 1.2,
    temp: '99.0℃',
    desc: '세척 및 살균 소독 완료된 원목 식기입니다.',
    img: 'https://images.unsplash.com/photo-1576201836106-db1758fd1c97?w=500&auto=format&fit=crop&q=80'
  }
];

// Sitter Profiles Initial Dataset
const DEFAULT_SITTER_PROFILES = [
  {
    id: 1,
    name: '김은지 펫시터',
    certs: '반려동물관리사 1급 • 반려경력 10년 • 300회 무사고 돌봄',
    appeal: '단독 케어 원칙으로 낯가림이나 분리불안이 있는 아이도 편안하게 쉴 수 있습니다. 30분마다 고화질 사진과 LIVE GPS 산책 일지를 보내드립니다.',
    envTags: ['24시 상주', '단독 케어', '슬개골 안심매트', '현관 안전문'],
    price: 71600,
    distance: '서울 강남구 역삼동 • 350m',
    distanceKm: 0.35,
    rating: 4.98,
    reviewCount: 42,
    aiScore: 99,
    aiReason: '우리 초코와의 안심 궁합 99%! (낯가림 적음 • 실내 배변 완벽 일치)',
    houseImg: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&auto=format&fit=crop&q=80'
  },
  {
    id: 2,
    name: '박서준 전문훈련사',
    certs: '한국애견협회 1급 훈련사 • 행동교정 전문 • 대형견/분리불안 전문',
    appeal: '300평 규모의 천연 잔디 마당에서 안전한 1:1 맞춤 분리불안 완화 놀이를 진행합니다. 짖음 교정이 필요한 아이도 환영합니다.',
    envTags: ['전문 훈련사', '천연잔디 마당', '행동교정 코칭', '24시 CCTV'],
    price: 88000,
    distance: '서울 강남구 역삼동 • 720m',
    distanceKm: 0.72,
    rating: 5.0,
    reviewCount: 68,
    aiScore: 95,
    aiReason: '우리 초코와의 안심 궁합 95%! (분리불안 집중 케어 & 천연 잔디 마당)',
    houseImg: 'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=600&auto=format&fit=crop&q=80'
  }
];

// Owner Requests Initial Dataset
const DEFAULT_OWNER_REQUESTS = [
  {
    id: 201,
    petName: '초코',
    petBreed: '말티즈',
    petWeight: '3.4kg',
    petPersonality: '온순함, 낯가림 약간 있음',
    tags: ['단독 산책 2회', '정시 투약/안약', '30분 포토리포트'],
    desc: '주말 출장으로 하루 위탁 돌봄 부탁드립니다. 1견 단독 케어 펫시터님을 찾습니다!',
    schedule: '9/20(일) 13시~18시',
    budget: 45000,
    distance: '역삼1동 • 150m',
    distanceKm: 0.15,
    status: 'matching',
    ownerName: '김태훈',
    createdAt: '방금 전',
    proposals: [
      {
        id: 301,
        sitterName: '김은지 펫시터',
        sitterAvatar: '👩‍🦰',
        price: 45000,
        message: '안녕하세요 초코 보호자님! 1견 단독 케어 및 정시 투약, 30분 포토리포트 완벽 준수합니다.',
        createdAt: '10분 전'
      }
    ]
  }
];

let marketItems = JSON.parse(localStorage.getItem('멍당근_market_items')) || DEFAULT_MARKET_ITEMS;
let sitterProfiles = JSON.parse(localStorage.getItem('멍당근_sitter_profiles')) || DEFAULT_SITTER_PROFILES;
let ownerRequests = JSON.parse(localStorage.getItem('멍당근_owner_requests')) || DEFAULT_OWNER_REQUESTS;

// ================= 2. Core Initializer =================
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) lucide.createIcons();
  
  const today = new Date().toISOString().split('T')[0];
  const dateInput = document.getElementById('chart-date-input');
  if (dateInput) dateInput.value = today;

  renderChartHistory();
  renderMarketItems();
  renderBidirectionalSitterFeed();
  updateOwnerRequestBadge();
  updateLiveClock();
  setInterval(updateLiveClock, 30000);
});

function updateLiveClock() {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const el = document.getElementById('current-time');
  if (el) el.textContent = `${hours}:${minutes}`;
}

// ================= 3. Tab Switcher =================
window.switchTab = function(tabId) {
  const tabs = ['home', 'ai', 'compat', 'chart', 'settings'];
  const titles = {
    home: '멍당근',
    ai: '무료 AI 건강 스캐너',
    compat: '멍냥 케미 & 궁합 분석',
    chart: '스마트 닥터 차트',
    settings: '설정'
  };

  tabs.forEach(t => {
    const view = document.getElementById(`view-${t}`);
    const nav = document.getElementById(`nav-${t}`);
    if (t === tabId) {
      if (view) view.classList.remove('hidden');
      if (nav) {
        nav.classList.add('active', 'text-blue-600');
        nav.classList.remove('text-slate-400');
      }
    } else {
      if (view) view.classList.add('hidden');
      if (nav) {
        nav.classList.remove('active', 'text-blue-600');
        nav.classList.add('text-slate-400');
      }
    }
  });

  const headerTitle = document.getElementById('header-title');
  const backNav = document.getElementById('btn-back-nav');
  if (headerTitle) headerTitle.textContent = titles[tabId] || '멍당근';
  if (backNav) {
    if (tabId !== 'home') backNav.classList.remove('hidden');
    else backNav.classList.add('hidden');
  }

  if (window.lucide) lucide.createIcons();
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

window.switchAppMode = function(mode) {
  currentAppMode = mode;
  const btnOwner = document.getElementById('btn-mode-owner');
  const btnSitter = document.getElementById('btn-mode-sitter');
  if (mode === 'owner') {
    if (btnOwner) {
      btnOwner.classList.add('bg-white', 'text-blue-600', 'shadow-sm');
      btnOwner.classList.remove('text-slate-500');
    }
    if (btnSitter) {
      btnSitter.classList.remove('bg-white', 'text-blue-600', 'shadow-sm');
      btnSitter.classList.add('text-slate-500');
    }
    switchSitterFeedTab('requests');
  } else {
    if (btnSitter) {
      btnSitter.classList.add('bg-white', 'text-blue-600', 'shadow-sm');
      btnSitter.classList.remove('text-slate-500');
    }
    if (btnOwner) {
      btnOwner.classList.remove('bg-white', 'text-blue-600', 'shadow-sm');
      btnOwner.classList.add('text-slate-500');
    }
    switchSitterFeedTab('sitters');
  }
};

// ================= 4. Sitter & Owner Bidirectional Feed =================
window.switchSitterFeedTab = function(tab) {
  currentSitterFeedTab = tab;
  const btnSitters = document.getElementById('tab-btn-sitter-list');
  const btnRequests = document.getElementById('tab-btn-owner-requests');
  const actionBtnBox = document.getElementById('sitter-feed-action-btn-box');

  if (tab === 'sitters') {
    if (btnSitters) {
      btnSitters.classList.add('bg-white', 'text-blue-600', 'shadow-sm');
      btnSitters.classList.remove('text-slate-500');
    }
    if (btnRequests) {
      btnRequests.classList.remove('bg-white', 'text-blue-600', 'shadow-sm');
      btnRequests.classList.add('text-slate-500');
    }
    if (actionBtnBox) {
      actionBtnBox.innerHTML = `
        <button onclick="openSitterProfileWriteModal()" class="flex items-center gap-1 px-3 py-1.5 rounded-full bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-black shadow-xs transition-transform active:scale-95">
          <i data-lucide="plus" class="w-3.5 h-3.5"></i>
          <span>펫시터 등록</span>
        </button>
      `;
    }
  } else {
    if (btnRequests) {
      btnRequests.classList.add('bg-white', 'text-blue-600', 'shadow-sm');
      btnRequests.classList.remove('text-slate-500');
    }
    if (btnSitters) {
      btnSitters.classList.remove('bg-white', 'text-blue-600', 'shadow-sm');
      btnSitters.classList.add('text-slate-500');
    }
    if (actionBtnBox) {
      actionBtnBox.innerHTML = `
        <button onclick="openOwnerRequestWriteModal()" class="flex items-center gap-1 px-3 py-1.5 rounded-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-black shadow-xs transition-transform active:scale-95">
          <i data-lucide="plus" class="w-3.5 h-3.5"></i>
          <span>돌봄 구해요</span>
        </button>
      `;
    }
  }

  updateOwnerRequestBadge();
  renderBidirectionalSitterFeed();
  if (window.lucide) lucide.createIcons();
};

function updateOwnerRequestBadge() {
  const badge = document.getElementById('owner-request-count-badge');
  if (badge) {
    const count = ownerRequests.filter(r => r.status === 'matching').length;
    badge.textContent = `${count}건`;
  }
}

window.renderBidirectionalSitterFeed = function() {
  const container = document.getElementById('sitter-bidirectional-feed-container');
  if (!container) return;

  if (currentSitterFeedTab === 'sitters') {
    container.innerHTML = sitterProfiles.map(sitter => `
      <div class="pet-card rounded-3xl overflow-hidden border border-slate-100 shadow-sm hover:border-blue-300 transition-all">
        <div class="relative h-44 bg-slate-200 overflow-hidden">
          <img src="${sitter.houseImg}" alt="돌봄 환경" class="w-full h-full object-cover">
          <div class="absolute top-3 left-3 flex gap-1.5">
            <span class="bg-blue-600 text-white font-black text-[10px] px-2.5 py-0.5 rounded-full shadow">${sitter.envTags[0] || '단독 케어'}</span>
            <span class="bg-emerald-600 text-white font-black text-[10px] px-2.5 py-0.5 rounded-full shadow">${sitter.envTags[1] || '24시 상주'}</span>
          </div>
        </div>

        <div class="p-4 space-y-2.5">
          <div class="flex items-center justify-between">
            <div>
              <div class="flex items-center gap-1.5">
                <h4 class="font-black text-sm text-slate-900">${sitter.name}</h4>
                <span class="text-xs font-bold text-amber-500">⭐ ${sitter.rating} (${sitter.reviewCount})</span>
              </div>
              <p class="text-[11px] text-slate-500 mt-0.5">${sitter.distance}</p>
            </div>
            <div class="text-right">
              <span class="text-[10px] text-slate-400">1박 돌봄</span>
              <p class="text-base font-black text-slate-900">${sitter.price.toLocaleString()}원</p>
            </div>
          </div>

          <p class="text-[11px] text-slate-600 bg-slate-50 p-2.5 rounded-2xl border border-slate-100">
            "${sitter.appeal}"
          </p>

          <div class="p-2.5 bg-blue-50/80 rounded-2xl border border-blue-100 flex items-center justify-between">
            <span class="text-[11px] font-black text-blue-700">✨ AI 안심 궁합 ${sitter.aiScore}% (${sitter.aiReason})</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-blue-600 text-white font-bold shrink-0">찰떡매칭</span>
          </div>

          <div class="flex gap-2 pt-1">
            <button onclick="openLiveWalkGpsModal('초코', '${sitter.name}')" class="flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-2xl text-xs flex items-center justify-center gap-1">
              <i data-lucide="navigation" class="w-3.5 h-3.5 text-blue-600"></i>
              <span>산책 LIVE GPS</span>
            </button>
            <button onclick="openCareContractModal(null, ${sitter.id}, ${sitter.price}, '2026-09-20 (13:00~18:00)')" class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl text-xs shadow-sm">
              1:1 안심 돌봄 예약
            </button>
          </div>
        </div>
      </div>
    `).join('');
  } else {
    container.innerHTML = ownerRequests.map(req => `
      <div class="pet-card rounded-3xl p-4 border border-orange-200/80 bg-gradient-to-b from-orange-50/30 via-white to-white shadow-sm space-y-3">
        <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
          <div class="flex items-center gap-2.5">
            <div class="w-12 h-12 rounded-2xl bg-orange-100 flex items-center justify-center text-2xl shadow-inner">
              🐕
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <h4 class="font-black text-sm text-slate-900">${req.petName} (${req.petBreed} • ${req.petWeight})</h4>
                <span class="text-[9px] bg-orange-600 text-white font-black px-1.5 py-0.2 rounded-full">${req.status === 'matching' ? '지원 접수중' : '계약 완료'}</span>
              </div>
              <p class="text-[10px] text-slate-400 mt-0.5">${req.ownerName} 보호자 • ${req.distance}</p>
            </div>
          </div>
          <div class="text-right">
            <span class="text-[10px] text-slate-400 block">희망 예산</span>
            <span class="text-sm font-black text-orange-600">${req.budget.toLocaleString()}원</span>
          </div>
        </div>

        <div class="p-2.5 bg-amber-50 rounded-2xl border border-amber-200 flex items-center justify-between text-xs">
          <span class="font-bold text-amber-900">📅 희망 일정: ${req.schedule}</span>
        </div>

        <div class="flex flex-wrap gap-1">
          ${req.tags.map(t => `<span class="text-[10px] font-bold bg-blue-50 text-blue-700 px-2 py-0.5 rounded-lg border border-blue-200">✓ ${t}</span>`).join('')}
        </div>

        <p class="text-slate-700 text-[11px] bg-slate-50 p-2.5 rounded-2xl border border-slate-100">
          "${req.desc}"
        </p>

        <div class="pt-1 border-t border-slate-100 space-y-1.5">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-slate-700">💌 지원 펫시터 (${req.proposals.length}명)</span>
            ${req.status === 'matching' ? `
              <button onclick="openSitterProposalModal(${req.id})" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-[10px] font-black">
                + 나도 맞춤 지원하기
              </button>
            ` : ''}
          </div>

          ${req.proposals.map(p => `
            <div class="p-2.5 bg-blue-50/70 rounded-xl border border-blue-100 text-xs flex items-center justify-between">
              <div>
                <span class="font-bold text-slate-800">${p.sitterName}</span>
                <span class="text-[10px] text-blue-600 font-bold ml-1">${p.price.toLocaleString()}원 제안</span>
                <p class="text-[10px] text-slate-500 mt-0.5">"${p.message}"</p>
              </div>
              ${req.status === 'matching' ? `
                <button onclick="openCareContractModal(${req.id}, 1, ${p.price}, '${req.schedule}')" class="px-2.5 py-1 bg-blue-600 text-white rounded-lg text-[10px] font-black">
                  계약하기
                </button>
              ` : '<span class="text-[10px] text-emerald-600 font-bold">계약완료</span>'}
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
  }
  if (window.lucide) lucide.createIcons();
};

// ================= 5. Market Logic & Voice Alerts =================
window.setMarketRadius = function(radius, btn) {
  currentMarketRadius = radius;
  document.querySelectorAll('#radius-btn-group .radius-pill-btn').forEach(b => {
    b.classList.remove('active', 'bg-orange-600', 'text-white', 'font-black');
    b.classList.add('bg-white', 'text-slate-700', 'font-bold');
  });
  if (btn) {
    btn.classList.add('active', 'bg-orange-600', 'text-white', 'font-black');
    btn.classList.remove('bg-white', 'text-slate-700', 'font-bold');
  }
  const badge = document.getElementById('market-current-radius-badge');
  if (badge) badge.textContent = radius === 'all' ? '반경 전체' : `반경 ${radius}km`;
  renderMarketItems();
};

window.filterMarketCategory = function(cat, btn) {
  currentMarketFilter = cat;
  document.querySelectorAll('.market-tab-btn').forEach(b => b.classList.remove('active', 'bg-blue-50', 'text-blue-700'));
  if (btn) btn.classList.add('active', 'bg-blue-50', 'text-blue-700');
  renderMarketItems();
};

function renderMarketItems() {
  const container = document.getElementById('market-items-container');
  if (!container) return;

  let filtered = marketItems;
  if (currentMarketRadius !== 'all') {
    filtered = filtered.filter(i => i.distanceKm <= parseFloat(currentMarketRadius));
  }
  if (currentMarketFilter === 'free') {
    filtered = filtered.filter(i => i.type === 'free');
  } else if (currentMarketFilter !== 'all' && currentMarketFilter !== 'fit') {
    filtered = filtered.filter(i => i.category === currentMarketFilter);
  }

  const neighborhoodText = document.getElementById('market-neighborhood-text');
  if (neighborhoodText) {
    neighborhoodText.textContent = `📍 역삼1동 기준 • 반경 ${currentMarketRadius}km 내 ${filtered.length}개 나눔/물품 탐색`;
  }

  container.innerHTML = filtered.map(item => `
    <div onclick="openMarketDetailModal(${item.id})" class="p-3 bg-white rounded-2xl border border-slate-100 hover:border-orange-300 shadow-xs flex gap-3 cursor-pointer transition-all active:scale-99">
      <div class="w-20 h-20 rounded-xl bg-slate-100 overflow-hidden shrink-0 relative">
        <img src="${item.img}" class="w-full h-full object-cover">
        ${item.type === 'free' ? '<span class="absolute top-1 left-1 bg-rose-500 text-white text-[9px] font-black px-1.5 py-0.2 rounded-md shadow">나눔 🎁</span>' : ''}
      </div>
      <div class="flex-1 min-w-0 flex flex-col justify-between">
        <div>
          <h4 class="font-bold text-xs text-slate-900 truncate">${item.title}</h4>
          <p class="text-[10px] text-slate-400 mt-0.5">${item.seller} • ${item.distance}</p>
        </div>
        <div class="flex items-center justify-between mt-1">
          <span class="text-xs font-black ${item.type === 'free' ? 'text-rose-500' : 'text-slate-900'}">
            ${item.type === 'free' ? '0원 (무료나눔)' : item.price.toLocaleString() + '원'}
          </span>
          <span class="text-[9px] text-orange-600 bg-orange-50 px-1.5 py-0.5 rounded font-bold">${item.temp}</span>
        </div>
      </div>
    </div>
  `).join('');
}

// 5-Year-Old Girl Voice Player
window.play5YoGirlVoice = function(voiceId) {
  const targetId = voiceId || selectedVoiceId || 1;
  const audioFile = `mung_voice_${targetId}.mp3`;

  if (currentPreviewAudio) {
    currentPreviewAudio.pause();
    currentPreviewAudio.currentTime = 0;
  }

  try {
    currentPreviewAudio = new Audio(audioFile);
    currentPreviewAudio.volume = 1.0;
    currentPreviewAudio.play().catch(err => {
      console.log('Audio file play fallback to Web Speech:', err);
      fallbackTTS();
    });
  } catch (e) {
    fallbackTTS();
  }
};

function fallbackTTS() {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance('멍 당근!');
    utterance.lang = 'ko-KR';
    utterance.pitch = 1.8;
    utterance.rate = 1.4;
    window.speechSynthesis.speak(utterance);
  }
}

window.toggleMungVoiceAlarm = function() {
  isMungVoiceAlarmEnabled = !isMungVoiceAlarmEnabled;
  const statusEl = document.getElementById('voice-alarm-status-text');
  if (statusEl) statusEl.textContent = isMungVoiceAlarmEnabled ? '음성 알람: ON' : '음성 알람: OFF (무음)';
  alert(isMungVoiceAlarmEnabled ? '🔔 [음성 알람 ON] 5살 여아 "멍당근" 음성 알람이 켜졌습니다!' : '🔕 [음성 알람 OFF] 무음 모드로 전환되었습니다.');
};

window.testMungDanggeunVoiceAlarm = function() {
  playMungDanggeunVoiceAlert('3.5kg 소형견 겨울 패딩 나눔 도착!');
};

window.playMungDanggeunVoiceAlert = function(title) {
  if (isMungVoiceAlarmEnabled) {
    play5YoGirlVoice(selectedVoiceId);
  }

  const banner = document.getElementById('mungdanggeun-alarm-banner');
  const titleEl = document.getElementById('alarm-banner-title');
  if (banner && titleEl) {
    titleEl.textContent = title || '새로운 무료 나눔 물품 도착!';
    banner.classList.add('opacity-100', 'translate-y-0');
    banner.classList.remove('opacity-0', '-translate-y-28');

    if (bannerDismissTimer) clearTimeout(bannerDismissTimer);
    bannerDismissTimer = setTimeout(() => {
      dismissAlarmBanner();
    }, 4500);
  }
};

window.dismissAlarmBanner = function() {
  const banner = document.getElementById('mungdanggeun-alarm-banner');
  if (banner) {
    banner.classList.remove('opacity-100', 'translate-y-0');
    banner.classList.add('opacity-0', '-translate-y-28');
  }
};

window.handleAlarmBannerClick = function() {
  dismissAlarmBanner();
  openMarketDetailModal(1);
};

// Voice Selector Modal
window.openVoiceSelectorModal = function() {
  tempSelectedVoiceId = selectedVoiceId;
  const container = document.getElementById('voice-options-list');
  if (container) {
    container.innerHTML = MUNG_VOICE_OPTIONS.map(opt => `
      <div onclick="selectVoiceOption(${opt.id})" class="p-3 rounded-2xl border ${opt.id === tempSelectedVoiceId ? 'border-orange-500 bg-orange-50/70 ring-2 ring-orange-400' : 'border-slate-100 bg-white'} flex items-center justify-between cursor-pointer">
        <div>
          <div class="flex items-center gap-1.5">
            <h4 class="font-bold text-xs text-slate-800">${opt.title}</h4>
            <span class="text-[9px] px-1.5 py-0.2 rounded-md font-bold ${opt.id === tempSelectedVoiceId ? 'bg-orange-600 text-white' : 'bg-slate-100 text-slate-500'}">${opt.tag}</span>
          </div>
          <p class="text-[10px] text-slate-400 mt-0.5">${opt.desc}</p>
        </div>
        <button type="button" onclick="event.stopPropagation(); play5YoGirlVoice(${opt.id})" class="px-2.5 py-1.5 rounded-xl bg-orange-100 text-orange-700 text-xs font-black">
          ▶️ 듣기
        </button>
      </div>
    `).join('');
  }
  const modal = document.getElementById('modal-voice-selector');
  if (modal) modal.classList.remove('hidden');
};

window.closeVoiceSelectorModal = function() {
  const modal = document.getElementById('modal-voice-selector');
  if (modal) modal.classList.add('hidden');
};

window.selectVoiceOption = function(id) {
  tempSelectedVoiceId = id;
  openVoiceSelectorModal();
  play5YoGirlVoice(id);
};

window.confirmVoiceSelection = function() {
  selectedVoiceId = tempSelectedVoiceId;
  const badge = document.getElementById('current-voice-num-badge');
  if (badge) badge.textContent = `(${selectedVoiceId}번 선택)`;
  closeVoiceSelectorModal();
  play5YoGirlVoice(selectedVoiceId);
  alert(`🎉 ${selectedVoiceId}번 목소리로 알람 설정이 완료되었습니다!`);
};

// ================= 6. Modals Logic =================
window.openMarketWriteModal = function() {
  const modal = document.getElementById('modal-market-write');
  if (modal) modal.classList.remove('hidden');
};
window.closeMarketWriteModal = function() {
  const modal = document.getElementById('modal-market-write');
  if (modal) modal.classList.add('hidden');
};

window.selectMarketTradeMode = function(mode, btn) {
  currentSelectedTradeMode = mode;
  document.querySelectorAll('.market-trade-btn').forEach(b => {
    b.classList.remove('bg-orange-500', 'text-white');
    b.classList.add('bg-slate-50', 'text-slate-700');
  });
  btn.classList.add('bg-orange-500', 'text-white');
  btn.classList.remove('bg-slate-50', 'text-slate-700');
  const priceBox = document.getElementById('market-price-box');
  if (priceBox) {
    if (mode === 'sale') priceBox.classList.remove('hidden');
    else priceBox.classList.add('hidden');
  }
};

window.submitMarketPost = function() {
  const title = document.getElementById('market-input-title').value.trim();
  const desc = document.getElementById('market-input-desc').value.trim();
  const cat = document.getElementById('market-input-cat').value;
  const price = document.getElementById('market-input-price') ? document.getElementById('market-input-price').value : '0';

  if (!title) {
    alert('제목을 입력해주세요!');
    return;
  }

  const newItem = {
    id: Date.now(),
    title: title,
    type: currentSelectedTradeMode,
    price: currentSelectedTradeMode === 'free' ? 0 : parseInt(price || '0'),
    category: cat,
    seller: '역삼1동 이웃 (초코 보호자)',
    distance: '150m (방금 등록)',
    distanceKm: 0.15,
    temp: '99.0℃',
    desc: desc || '깨끗하게 보관 중인 물품입니다.',
    img: 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=500&auto=format&fit=crop&q=80'
  };

  marketItems.unshift(newItem);
  localStorage.setItem('멍당근_market_items', JSON.stringify(marketItems));
  renderMarketItems();
  closeMarketWriteModal();
  playMungDanggeunVoiceAlert(title);
  alert('🎉 나눔 물품이 등록되었습니다!');
};

window.openMarketDetailModal = function(id) {
  const item = marketItems.find(i => i.id === id) || marketItems[0];
  const modal = document.getElementById('modal-market-detail');
  if (modal && item) {
    document.getElementById('detail-market-img').src = item.img;
    document.getElementById('detail-seller-name').textContent = item.seller;
    document.getElementById('detail-market-title').textContent = item.title;
    document.getElementById('detail-market-price').textContent = item.type === 'free' ? '0원 (무료나눔)' : item.price.toLocaleString() + '원';
    document.getElementById('detail-market-desc').textContent = item.desc;
    modal.classList.remove('hidden');
  }
};
window.closeMarketDetailModal = function() {
  const modal = document.getElementById('modal-market-detail');
  if (modal) modal.classList.add('hidden');
};

window.startMarketChat = function() {
  alert('💬 [1:1 멍채팅 연결]\n"안녕하세요! 나눔 문의드립니다." 메시지를 보냈습니다.');
};

window.openOwnerRequestWriteModal = function() {
  const modal = document.getElementById('modal-owner-request-write');
  if (modal) modal.classList.remove('hidden');
};
window.closeOwnerRequestWriteModal = function() {
  const modal = document.getElementById('modal-owner-request-write');
  if (modal) modal.classList.add('hidden');
};

window.toggleRequestTag = function(btn, tag) {
  if (tempReqCareTags.includes(tag)) {
    tempReqCareTags = tempReqCareTags.filter(t => t !== tag);
    btn.classList.remove('bg-blue-50', 'border-blue-300', 'text-blue-700');
    btn.classList.add('bg-slate-50', 'border-slate-200', 'text-slate-700');
  } else {
    tempReqCareTags.push(tag);
    btn.classList.add('bg-blue-50', 'border-blue-300', 'text-blue-700');
    btn.classList.remove('bg-slate-50', 'border-slate-200', 'text-slate-700');
  }
};

window.submitOwnerRequest = function() {
  const schedule = document.getElementById('req-input-schedule').value.trim();
  const budget = document.getElementById('req-input-budget').value.trim();
  const desc = document.getElementById('req-input-desc').value.trim();

  if (!schedule || !budget) {
    alert('일정과 예산을 입력해주세요!');
    return;
  }

  const newReq = {
    id: Date.now(),
    petName: currentPet.name,
    petBreed: currentPet.breed,
    petWeight: currentPet.weight,
    petPersonality: '온순함, 사람을 매우 좋아함',
    tags: [...tempReqCareTags],
    desc: desc || '정성스럽게 돌봐주실 펫시터님을 찾습니다.',
    schedule: schedule,
    budget: parseInt(budget),
    distance: '역삼1동 • 방금 등록',
    distanceKm: 0.1,
    status: 'matching',
    ownerName: '김태훈',
    createdAt: '방금 전',
    proposals: []
  };

  ownerRequests.unshift(newReq);
  localStorage.setItem('멍당근_owner_requests', JSON.stringify(ownerRequests));
  closeOwnerRequestWriteModal();
  switchSitterFeedTab('requests');
  playMungDanggeunVoiceAlert(`[돌봄 구해요] ${newReq.petName}의 돌봄 의뢰서 도착! 🐕`);
  alert('🎉 맞춤 돌봄 의뢰서가 등록되었습니다!');
};

window.openSitterProfileWriteModal = function() {
  const modal = document.getElementById('modal-sitter-profile-write');
  if (modal) modal.classList.remove('hidden');
};
window.closeSitterProfileWriteModal = function() {
  const modal = document.getElementById('modal-sitter-profile-write');
  if (modal) modal.classList.add('hidden');
};

window.submitSitterProfile = function() {
  const name = document.getElementById('sitter-write-name').value.trim();
  const certs = document.getElementById('sitter-write-certs').value.trim();
  const price = document.getElementById('sitter-write-price').value.trim();
  const appeal = document.getElementById('sitter-write-appeal').value.trim();
  const radius = document.getElementById('sitter-write-radius').value;

  if (!name || !price) {
    alert('이름과 요금을 입력해주세요!');
    return;
  }

  const newSitter = {
    id: Date.now(),
    name: name,
    certs: certs || '반려동물관리사 • 반려생활 10년',
    appeal: appeal || '아이의 안전과 편안한 휴식을 최우선으로 돌봅니다.',
    envTags: ['24시 상주', '단독 케어', '안심매트'],
    price: parseInt(price),
    distance: `역삼동 • 반경 ${radius}km`,
    distanceKm: parseFloat(radius),
    rating: 5.0,
    reviewCount: 1,
    aiScore: 98,
    aiReason: '우리 초코와의 안심 궁합 98%!',
    houseImg: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&auto=format&fit=crop&q=80'
  };

  sitterProfiles.unshift(newSitter);
  localStorage.setItem('멍당근_sitter_profiles', JSON.stringify(sitterProfiles));
  closeSitterProfileWriteModal();
  switchSitterFeedTab('sitters');
  alert(`🎉 [${name}] 펫시터 프로필이 등록되었습니다!`);
};

window.openSitterProposalModal = function(requestId) {
  currentTargetRequestId = requestId;
  const req = ownerRequests.find(r => r.id === requestId);
  const targetBox = document.getElementById('proposal-target-request-box');
  if (targetBox && req) {
    targetBox.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="font-bold text-slate-800">🐕 ${req.petName} (${req.petWeight})</span>
        <span class="font-black text-orange-600">${req.budget.toLocaleString()}원</span>
      </div>
      <p class="text-[11px] text-slate-500">일정: ${req.schedule}</p>
    `;
  }
  const modal = document.getElementById('modal-sitter-proposal-write');
  if (modal) modal.classList.remove('hidden');
};
window.closeSitterProposalModal = function() {
  const modal = document.getElementById('modal-sitter-proposal-write');
  if (modal) modal.classList.add('hidden');
};

window.submitSitterProposal = function() {
  const price = document.getElementById('proposal-input-price').value.trim();
  const message = document.getElementById('proposal-input-message').value.trim();
  const req = ownerRequests.find(r => r.id === currentTargetRequestId);
  if (!req) return;

  req.proposals.unshift({
    id: Date.now(),
    sitterName: '김은지 펫시터',
    sitterAvatar: '👩‍🦰',
    price: parseInt(price || req.budget.toString()),
    message: message || '요청하신 케어 완벽히 수행하겠습니다!',
    createdAt: '방금 전'
  });

  localStorage.setItem('멍당근_owner_requests', JSON.stringify(ownerRequests));
  closeSitterProposalModal();
  renderBidirectionalSitterFeed();
  playMungDanggeunVoiceAlert(`[맞춤 지원 완료] 제안서가 전송되었습니다! 🥕`);
  alert('🎉 맞춤 케어 제안서가 전송되었습니다!');
};

window.openCareContractModal = function(requestId, sitterId, price, schedule) {
  const req = requestId ? ownerRequests.find(r => r.id === requestId) : null;
  const sitter = sitterId ? sitterProfiles.find(s => s.id === sitterId) : sitterProfiles[0];

  currentContractContext = {
    requestId: requestId,
    petInfo: req ? `${req.petName} (${req.petWeight})` : `${currentPet.name} (${currentPet.weight})`,
    sitterName: sitter ? sitter.name : '김은지 펫시터',
    schedule: schedule || '2026-09-20 (13:00 ~ 18:00)',
    price: price || 45000
  };

  const elPetInfo = document.getElementById('contract-pet-info');
  const elSitterName = document.getElementById('contract-sitter-name');
  const elSchedule = document.getElementById('contract-schedule');
  const elPrice = document.getElementById('contract-price');

  if (elPetInfo) elPetInfo.textContent = currentContractContext.petInfo;
  if (elSitterName) elSitterName.textContent = currentContractContext.sitterName;
  if (elSchedule) elSchedule.textContent = currentContractContext.schedule;
  if (elPrice) elPrice.textContent = `${currentContractContext.price.toLocaleString()}원`;

  const modal = document.getElementById('modal-care-contract');
  if (modal) modal.classList.remove('hidden');
};
window.closeCareContractModal = function() {
  const modal = document.getElementById('modal-care-contract');
  if (modal) modal.classList.add('hidden');
};

window.confirmCareContractExecution = function() {
  if (currentContractContext && currentContractContext.requestId) {
    const req = ownerRequests.find(r => r.id === currentContractContext.requestId);
    if (req) {
      req.status = 'contracted';
      localStorage.setItem('멍당근_owner_requests', JSON.stringify(ownerRequests));
    }
  }

  closeCareContractModal();
  renderBidirectionalSitterFeed();
  updateOwnerRequestBadge();
  play5YoGirlVoice(selectedVoiceId);
  openKakaoAlimtalkModal();
  alert('🎉 [돌봄 안심 계약 체결 완료!]\n카카오 알림톡으로 계약서가 발송되었습니다!');
};

window.openKakaoAlimtalkModal = function() {
  const modal = document.getElementById('modal-kakao-alimtalk');
  if (modal) modal.classList.remove('hidden');
};
window.closeKakaoAlimtalkModal = function() {
  const modal = document.getElementById('modal-kakao-alimtalk');
  if (modal) modal.classList.add('hidden');
};
window.handleKakaoChannelAdd = function() {
  alert('💬 [카카오톡 채널 추가]\n"멍당근 공식 채널이 추가되었습니다. 3,000원 웰컴 쿠폰이 지급되었습니다!"');
};

window.openPetProfileModal = function() {
  const modal = document.getElementById('modal-pet-profile');
  if (modal) modal.classList.remove('hidden');
};
window.closePetProfileModal = function() {
  const modal = document.getElementById('modal-pet-profile');
  if (modal) modal.classList.add('hidden');
};
window.savePetProfile = function() {
  const name = document.getElementById('input-pet-name').value.trim();
  const breed = document.getElementById('input-pet-breed').value.trim();
  const weight = document.getElementById('input-pet-weight').value.trim();
  if (name) currentPet.name = name;
  if (breed) currentPet.breed = breed;
  if (weight) currentPet.weight = weight;

  const elName = document.getElementById('home-pet-name');
  const elSub = document.getElementById('home-pet-subtext');
  if (elName) elName.textContent = currentPet.name;
  if (elSub) elSub.textContent = `${currentPet.breed} • 3세 • ${currentPet.weight}`;

  closePetProfileModal();
  alert('🐶 아이 정보가 수정되었습니다!');
};

window.openAuthModal = function() {
  const modal = document.getElementById('modal-auth');
  if (modal) modal.classList.remove('hidden');
};
window.closeAuthModal = function() {
  const modal = document.getElementById('modal-auth');
  if (modal) modal.classList.add('hidden');
};
window.loginWithKakao = function() {
  currentUser = { name: '김태훈', email: 'user@kakao.com', provider: 'kakao' };
  const authLabel = document.getElementById('header-auth-label');
  const userDisp = document.getElementById('user-display-name');
  if (authLabel) authLabel.textContent = '내계정';
  if (userDisp) userDisp.textContent = '김태훈 보호자님';
  closeAuthModal();
  alert('🎉 카카오 1초 로그인 성공! 평생 무제한 무료 이용이 적용되었습니다.');
};
window.loginWithGoogle = function() {
  loginWithKakao();
};

window.openLiveWalkGpsModal = function() {
  const modal = document.getElementById('modal-live-walk-gps');
  if (modal) modal.classList.remove('hidden');
};
window.closeLiveWalkGpsModal = function() {
  const modal = document.getElementById('modal-live-walk-gps');
  if (modal) modal.classList.add('hidden');
};

// ================= 7. AI Scanner & Compat & Chart =================
window.triggerAIScan = function() {
  const dropzone = document.getElementById('ai-dropzone');
  const resultBox = document.getElementById('ai-result-box');
  if (!dropzone || !resultBox) return;

  dropzone.innerHTML = `
    <div class="py-4 space-y-2">
      <div class="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p class="text-xs font-bold text-blue-600">Gemini 비전 AI 분석 중...</p>
    </div>
  `;

  setTimeout(() => {
    dropzone.innerHTML = `
      <div class="text-center py-2">
        <span class="text-2xl">🔍</span>
        <p class="text-xs font-bold text-emerald-600">분석 완료 (터치 시 재촬영)</p>
      </div>
    `;
    resultBox.classList.remove('hidden');
  }, 1000);
};

window.addAIResultToChart = function() {
  healthLogs.unshift({
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    appetite: '정상',
    stool: '정상변',
    symptoms: ['가려움/긁음'],
    memo: '[AI 진단 자동 기록] 피부 발진 및 지루성 피부염 88% 의심 소견'
  });
  renderChartHistory();
  alert('✅ AI 분석 결과가 닥터 차트에 기록되었습니다.');
  switchTab('chart');
};

window.simulateVoiceAnalysis = function() {
  const btn = document.getElementById('btn-voice-record');
  const res = document.getElementById('voice-analysis-result');
  if (btn && res) {
    btn.innerHTML = '<span class="animate-pulse">🎙️ 5초간 소리를 듣고 있습니다...</span>';
    setTimeout(() => {
      btn.innerHTML = '<span>다시 녹음하기</span>';
      res.classList.remove('hidden');
      res.textContent = '🔊 번역 결과: "지금 산책 가고 싶어요! 🐾" (기쁨 92%)';
    }, 1200);
  }
};

window.openCompatibilityModal = function() {
  const modal = document.getElementById('modal-compatibility');
  if (modal) modal.classList.remove('hidden');
};
window.closeCompatibilityModal = function() {
  const modal = document.getElementById('modal-compatibility');
  if (modal) modal.classList.add('hidden');
};
window.calcCompatibility = function() {
  const select = document.getElementById('compat-partner-select');
  const partner = select ? select.value : 'poodle';
  const data = {
    poodle: { score: '96%', title: '"찰떡궁합! 평생 단짝 베프"', desc: '초코의 활발함과 뽀삐의 다정함이 완벽히 조화됩니다.' },
    retriever: { score: '88%', title: '"든든한 맏형과 막내 케미"', desc: '몽이의 의젓함이 초코에게 안정감을 줍니다.' },
    cat_luna: { score: '72%', title: '"밀당하는 톰과 제리"', desc: '루나의 독립적 성향에 맞춰 거리를 조절합니다.' },
    corgi: { score: '91%', title: '"우다다 에너지 콤비"', desc: '신나게 뛰어놀 수 있는 최고의 놀이 메이트입니다.' }
  };
  const item = data[partner] || data.poodle;
  const resultBox = document.getElementById('compat-result-box');
  if (resultBox) {
    resultBox.innerHTML = `
      <div class="text-2xl font-black text-rose-600">케미 지수 ${item.score} 💕</div>
      <p class="text-xs font-bold text-slate-800">${item.title}</p>
      <p class="text-[11px] text-slate-500">${item.desc}</p>
    `;
  }
};
window.shareCompatResult = function() {
  alert('💬 [카카오톡 공유]\n궁합 결과가 카카오톡 친구에게 전송되었습니다!');
};

window.selectCheck = function(btn, type, val) {
  if (type === 'appetite') currentSelectedAppetite = val;
  if (type === 'stool') currentSelectedStool = val;
  const parent = btn.parentElement;
  parent.querySelectorAll('button').forEach(b => {
    b.classList.remove('bg-blue-600', 'text-white', 'font-bold');
  });
  btn.classList.add('bg-blue-600', 'text-white', 'font-bold');
};

window.toggleMultiCheck = function(btn, val) {
  if (currentSelectedSymptoms.includes(val)) {
    currentSelectedSymptoms = currentSelectedSymptoms.filter(s => s !== val);
    btn.classList.remove('bg-rose-500', 'text-white', 'font-bold');
  } else {
    currentSelectedSymptoms.push(val);
    btn.classList.add('bg-rose-500', 'text-white', 'font-bold');
  }
};

window.saveHealthLog = function() {
  const date = document.getElementById('chart-date-input').value;
  const memo = document.getElementById('chart-memo-input').value.trim();
  healthLogs.unshift({
    id: Date.now(),
    date: date,
    appetite: currentSelectedAppetite,
    stool: currentSelectedStool,
    symptoms: [...currentSelectedSymptoms],
    memo: memo || '특이사항 없음'
  });
  renderChartHistory();
  document.getElementById('chart-memo-input').value = '';
  alert('📋 오늘의 건강 기록이 저장되었습니다!');
};

function renderChartHistory() {
  const container = document.getElementById('chart-history-list');
  if (!container) return;
  container.innerHTML = healthLogs.map(log => `
    <div class="p-3 bg-slate-50 rounded-2xl border border-slate-100 text-xs space-y-1">
      <div class="flex justify-between items-center font-bold">
        <span class="text-slate-800">📅 ${log.date}</span>
        <span class="text-blue-600">식욕: ${log.appetite} | 대변: ${log.stool}</span>
      </div>
      <p class="text-slate-600 text-[11px]">${log.memo}</p>
    </div>
  `).join('');
}

window.exportDoctorChartPDF = function() {
  alert('📄 [PDF 차트 출력]\n오늘의 건강 기록 차트가 PDF로 다운로드되었습니다.');
};

// ==========================================
// 🛡️ [LEGAL PROTECTION & TERMS SYSTEM]
// 서비스 이용약관, 개인정보처리방침, 에어커버 보증 규정 & 면책 조항
// ==========================================

const TERMS_DATA = {
  terms: {
    icon: '⚖️',
    title: '서비스 이용약관 & 법적 면책 조항',
    subtitle: '통신판매중개자 법적 지위 및 플랫폼 책임 제한 고지',
    html: `
      <div class="space-y-3">
        <div class="p-3 bg-blue-50/80 rounded-xl border border-blue-200">
          <p class="font-black text-blue-900 text-xs">📌 핵심 법적 고지 (전자상거래법 제20조 제2항 준용)</p>
          <p class="text-[11px] text-blue-800 mt-1 leading-relaxed">
            멍당근은 회원 상호 간의 펫용품 P2P 무료나눔 및 펫시터 1:1 돌봄 매칭을 연결하는 <b>통신판매중개자</b>이며, 회원 간의 개별 거래 및 돌봄 행위에 대한 당사자가 아닙니다.
          </p>
        </div>

        <div class="space-y-1.5">
          <h4 class="font-black text-slate-900 text-xs">제1조 (목적)</h4>
          <p class="text-[11px] text-slate-600">
            본 약관은 『멍당근』(이하 "회사" 또는 "플랫폼")이 제공하는 반려동물 돌봄 매칭 및 이웃 나눔 서비스의 이용조건 및 절차, 이용자와 회사의 권리·의무 및 책임사항을 규정함을 목적으로 합니다.
          </p>
        </div>

        <div class="space-y-1.5">
          <h4 class="font-black text-slate-900 text-xs">제2조 (통신판매중개자로서의 지위 및 면책 조항)</h4>
          <ul class="text-[11px] text-slate-600 list-disc list-inside space-y-1 leading-relaxed">
            <li>회사는 통신판매중개자로서 거래 당사자가 아니며, 회원 간 등록한 정보, 나눔 물품의 하자, 돌봄의 품질 등에 대하여 보증하지 아니합니다.</li>
            <li>회원 상호 간(견주-펫시터, 나눔자-수령자)에 발생하는 모든 계약 이행, 대금 지급, 분쟁, 손해배상 책임은 거래 당사자 본인에게 있습니다.</li>
            <li>회사는 천재지변, 이용자의 귀책사유로 인한 서비스 장애 또는 회원 간의 분쟁에 대해 고의 또는 중과실이 없는 한 책임을 지지 않습니다.</li>
          </ul>
        </div>

        <div class="space-y-1.5">
          <h4 class="font-black text-slate-900 text-xs">제3조 (디지털 안심 돌봄 계약서 체결 의무)</h4>
          <p class="text-[11px] text-slate-600">
            견주와 펫시터는 돌봄 시작 전 반드시 앱 내 제공되는 <b>'디지털 안심 돌봄 계약서'</b>를 작성 및 상호 서명해야 하며, 계약서 미작성으로 인한 사고에 대해서는 에어커버 보증 및 플랫폼 보호 혜택이 제한될 수 있습니다.
          </p>
        </div>

        <div class="space-y-1.5">
          <h4 class="font-black text-slate-900 text-xs">제4조 (금지 행위 및 계정 제재)</h4>
          <p class="text-[11px] text-slate-600">
            동물 학대, 허위 정보 기재, 불법 번식 및 판매, 노쇼(No-Show), 타인 명의 도용 행위 적발 시 사전 통보 없이 계정 영구 정지 및 법적 조치가 취해질 수 있습니다.
          </p>
        </div>
      </div>
    `
  },
  privacy: {
    icon: '🔒',
    title: '개인정보 처리방침 & 위치기반서비스',
    subtitle: '개인정보 보호법 및 위치정보의 보호 및 이용 등에 관한 법률 준수',
    html: `
      <div class="space-y-3">
        <div class="p-3 bg-emerald-50/80 rounded-xl border border-emerald-200">
          <p class="font-black text-emerald-900 text-xs">🛡️ 개인정보 최소 수집 & 실시간 위치 비저장 원칙</p>
          <p class="text-[11px] text-emerald-800 mt-1 leading-relaxed">
            멍당근은 서비스 운영에 필요한 최소한의 정보만을 처리하며, <b>사용자의 실시간 GPS 좌표를 외부 서버에 영구 보관하지 않습니다.</b>
          </p>
        </div>

        <div class="space-y-1.5">
          <h4 class="font-black text-slate-900 text-xs">제1조 (수집하는 개인정보 항목)</h4>
          <ul class="text-[11px] text-slate-600 list-disc list-inside space-y-1">
            <li><b>소셜 로그인 시:</b> 고유 식별자, 닉네임, 프로필 사진 URL, 이메일</li>
            <li><b>반려동물 프로필:</b> 이름, 견종/묘종, 나이, 체중, 건강 특이사항</li>
            <li><b>돌봄 계약 체결 시:</b> 비상 연락처, 대략적인 동네 주소</li>
          </ul>
        </div>

        <div class="space-y-1.5">
          <h4 class="font-black text-slate-900 text-xs">제2조 (위치기반서비스 이용 고지)</h4>
          <p class="text-[11px] text-slate-600 leading-relaxed">
            앱 내 동네 반경(1km, 3km, 5km, 10km) 필터 기능은 단말기 상에서 반경 내 게시글을 정렬하는 용도로만 일시 활용되며, 사용자의 이동 경로나 위치 이력은 서버에 수집·저장되지 않습니다.
          </p>
        </div>

        <div class="space-y-1.5">
          <h4 class="font-black text-slate-900 text-xs">제3조 (개인정보의 보유 및 파기)</h4>
          <p class="text-[11px] text-slate-600">
            회원의 개인정보는 회원 탈퇴 시 지체 없이 파기하며, 전자상거래법 등 관련 법령에 의해 보존할 필요가 있는 경우 해당 법정 기간 동안만 안전하게 분리 보관됩니다.
          </p>
        </div>
      </div>
    `
  },
  aircover: {
    icon: '🛡️',
    title: '에어커버 최대 500만원 안심 보증 규정',
    subtitle: '돌봄 중 예기치 못한 사고에 대한 표준 병원비 지원 기준',
    html: `
      <div class="space-y-3">
        <div class="p-3 bg-amber-50/80 rounded-xl border border-amber-200">
          <p class="font-black text-amber-900 text-xs">🏥 안심 100% 멍당근 에어커버 보증제</p>
          <p class="text-[11px] text-amber-800 mt-1 leading-relaxed">
            디지털 안심 돌봄 계약서를 체결하고 진행된 정식 매칭 중 반려동물에게 응급 사고가 발생한 경우, <b>사고당 최대 500만원 한도 내 실손 동물병원 치료비</b>를 지원합니다.
          </p>
        </div>

        <div class="space-y-1.5">
          <h4 class="font-black text-slate-900 text-xs">제1조 (보장 대상 및 요건)</h4>
          <ul class="text-[11px] text-slate-600 list-disc list-inside space-y-1 leading-relaxed">
            <li>멍당근 앱 내 <b>'디지털 안심 돌봄 계약서'</b>가 상호 서명 완료된 돌봄 건</li>
            <li>돌봄 시작 시간부터 종료 시간 사이에 발생한 급성 상해, 교상, 이물질 삼킴, 골절 등 외상성 사고</li>
          </ul>
        </div>

        <div class="space-y-1.5">
          <h4 class="font-black text-slate-900 text-xs">제2조 (보상 한도액)</h4>
          <p class="text-[11px] text-slate-600">
            동물병원 실제 진료비 및 처치비에 대하여 <b>사고당 최대 5,000,000원(500만원)</b> 한도 내 실비 지급 (자기부담금 3만원 제외 후 정산).
          </p>
        </div>

        <div class="space-y-1.5">
          <h4 class="font-black text-slate-900 text-xs">제3조 (보상 제외 기준 - 면책 사항)</h4>
          <ul class="text-[11px] text-slate-600 list-disc list-inside space-y-1 leading-relaxed">
            <li>돌봄 계약 전 이미 앓고 있던 <b>기저 질환(슬개골 탈구, 심장질환, 만성 피부염 등)</b>의 단순 악화</li>
            <li>보호자가 사전에 고지하지 않은 전염성 질환 또는 공격성으로 인한 사고</li>
            <li>보호자 또는 펫시터의 고의적 상해 행위 및 법령 위반</li>
            <li>플랫폼 외부에서 계약서 없이 구두로 진행된 비공식 사적 돌봄</li>
          </ul>
        </div>

        <div class="space-y-1.5">
          <h4 class="font-black text-slate-900 text-xs">제4조 (청구 및 심사 절차)</h4>
          <p class="text-[11px] text-slate-600">
            사고 발생 후 <b>48시간 이내</b> 앱 내 고객센터 접수 ➡️ 수의사 진단서 및 진료비 세부 영수증 제출 ➡️ 제휴 손해보험사 심사 후 7영업일 내 지급.
          </p>
        </div>
      </div>
    `
  }
};

window.openTermsModal = function(type) {
  const data = TERMS_DATA[type] || TERMS_DATA.terms;
  const modal = document.getElementById('modal-terms');
  const icon = document.getElementById('terms-modal-icon');
  const title = document.getElementById('terms-modal-title');
  const body = document.getElementById('terms-modal-body');

  if (icon) icon.textContent = data.icon;
  if (title) title.textContent = data.title;
  if (body) body.innerHTML = data.html;

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
// 💡 [ONBOARDING WALKTHROUGH CAROUSEL SYSTEM]
// 앱 최초 실행 가이드 & 스와이프 튜토리얼 (건너뛰기 / 다음 / 이전)
// ==========================================

let currentOnboardingSlide = 0;
const TOTAL_ONBOARDING_SLIDES = 4;

window.initOnboarding = function() {
  const hasSeen = localStorage.getItem('mungdanggeun_onboarding_seen');
  if (!hasSeen) {
    setTimeout(() => {
      openOnboardingModal(false);
    }, 400);
  }
  setupOnboardingSwipeGestures();
};

window.openOnboardingModal = function(force = false) {
  currentOnboardingSlide = 0;
  updateOnboardingUI();
  const modal = document.getElementById('modal-onboarding');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    if (window.lucide) lucide.createIcons();
  }
};

window.closeOnboardingModal = function() {
  const modal = document.getElementById('modal-onboarding');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};

window.skipOnboarding = function() {
  localStorage.setItem('mungdanggeun_onboarding_seen', 'true');
  closeOnboardingModal();
};

window.finishOnboarding = function() {
  localStorage.setItem('mungdanggeun_onboarding_seen', 'true');
  closeOnboardingModal();
  // Play greeting sound if available
  if (typeof playSelectedMungVoice === 'function') {
    playSelectedMungVoice();
  }
};

window.nextOnboardingSlide = function() {
  if (currentOnboardingSlide < TOTAL_ONBOARDING_SLIDES - 1) {
    currentOnboardingSlide++;
    updateOnboardingUI();
  } else {
    finishOnboarding();
  }
};

window.prevOnboardingSlide = function() {
  if (currentOnboardingSlide > 0) {
    currentOnboardingSlide--;
    updateOnboardingUI();
  }
};

window.goToOnboardingSlide = function(idx) {
  if (idx >= 0 && idx < TOTAL_ONBOARDING_SLIDES) {
    currentOnboardingSlide = idx;
    updateOnboardingUI();
  }
};

function updateOnboardingUI() {
  const slides = document.querySelectorAll('.onboarding-slide');
  slides.forEach((slide, idx) => {
    if (idx === currentOnboardingSlide) {
      slide.classList.remove('hidden');
      slide.classList.add('active');
    } else {
      slide.classList.add('hidden');
      slide.classList.remove('active');
    }
  });

  // Update step indicator
  const indicator = document.getElementById('onboarding-step-indicator');
  if (indicator) {
    indicator.textContent = `${currentOnboardingSlide + 1} / ${TOTAL_ONBOARDING_SLIDES}`;
  }

  // Update dots
  const dots = document.querySelectorAll('#onboarding-dots button');
  dots.forEach((dot, idx) => {
    if (idx === currentOnboardingSlide) {
      dot.className = 'w-6 h-2 rounded-full bg-orange-600 transition-all';
    } else {
      dot.className = 'w-2 h-2 rounded-full bg-slate-200 hover:bg-slate-300 transition-all';
    }
  });

  // Update Buttons
  const btnPrev = document.getElementById('btn-onboarding-prev');
  const btnNext = document.getElementById('btn-onboarding-next');
  const nextText = document.getElementById('onboarding-next-text');

  if (btnPrev) {
    if (currentOnboardingSlide === 0) {
      btnPrev.classList.add('hidden');
    } else {
      btnPrev.classList.remove('hidden');
    }
  }

  if (nextText) {
    if (currentOnboardingSlide === TOTAL_ONBOARDING_SLIDES - 1) {
      nextText.textContent = '멍당근 시작하기 🥕';
      if (btnNext) {
        btnNext.className = 'flex-1 py-3 bg-gradient-to-r from-orange-600 via-amber-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 text-white font-black rounded-2xl text-xs shadow-lg shadow-orange-500/30 transition-transform active:scale-95 flex items-center justify-center gap-1.5 animate-pulse';
      }
    } else {
      nextText.textContent = `다음 (${currentOnboardingSlide + 1}/${TOTAL_ONBOARDING_SLIDES})`;
      if (btnNext) {
        btnNext.className = 'flex-1 py-3 bg-gradient-to-r from-orange-600 to-amber-500 hover:from-orange-700 hover:to-amber-600 text-white font-black rounded-2xl text-xs shadow-md transition-transform active:scale-95 flex items-center justify-center gap-1';
      }
    }
  }

  if (window.lucide) lucide.createIcons();
}

// Touch / Swipe Gestures for Mobile
function setupOnboardingSwipeGestures() {
  const slider = document.getElementById('onboarding-slider');
  if (!slider) return;

  let startX = 0;
  let endX = 0;

  slider.addEventListener('touchstart', (e) => {
    startX = e.changedTouches[0].screenX;
  }, { passive: true });

  slider.addEventListener('touchend', (e) => {
    endX = e.changedTouches[0].screenX;
    handleSwipe();
  }, { passive: true });

  function handleSwipe() {
    const diff = endX - startX;
    if (Math.abs(diff) > 45) { // 45px threshold
      if (diff < 0) {
        // Swipe left -> Next
        nextOnboardingSlide();
      } else {
        // Swipe right -> Prev
        prevOnboardingSlide();
      }
    }
  }
}

// Ensure initOnboarding is called on startup
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initOnboarding();
  });
} else {
  initOnboarding();
}
