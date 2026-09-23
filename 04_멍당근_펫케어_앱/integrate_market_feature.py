import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"
style_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\style.css"
app_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\app.js"

# 1. Update style.css with Market/Karrot styles
with open(style_file, 'r', encoding='utf-8') as f:
    css = f.read()

market_css = """
/* Karrot / Market Badge & Styles */
.badge-karrot-free {
  background: linear-gradient(135deg, #ff6b6b, #ff8787);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(255, 107, 107, 0.3);
}

.badge-manner-temp {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: #ffffff;
}

.market-tab-btn.active {
  background-color: #3b82f6 !important;
  color: #ffffff !important;
  font-weight: 800;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
}
"""

if '/* Karrot / Market Badge & Styles' not in css:
    css = css + "\n" + market_css
    with open(style_file, 'w', encoding='utf-8') as f:
        f.write(css)

print("style.css updated with market styling.")

# 2. Update index.html: Add Market Feed in Home & Add Market Nav Tab & Add Market Modals
with open(index_file, 'r', encoding='utf-8') as f:
    html = f.read()

# Add Market Section in Home View
home_market_section = """
        <!-- 🥕 [PET MARKET] 멍당근 - 동네 펫용품 무료나눔 & 중고거래 장터 -->
        <div class="pet-card rounded-3xl p-4 border border-orange-100 shadow-sm space-y-3 bg-gradient-to-b from-orange-50/40 via-white to-white">
          <div class="flex items-center justify-between px-1">
            <div class="flex items-center gap-2">
              <span class="text-2xl">🥕</span>
              <div>
                <div class="flex items-center gap-1.5">
                  <h3 class="text-base font-black text-slate-900">멍당근 동네 나눔장터</h3>
                  <span class="text-[9px] bg-orange-500 text-white font-black px-1.5 py-0.2 rounded-full">반경 1km</span>
                </div>
                <p class="text-[11px] text-slate-400">작아진 옷, 남은 사료, 장난감 무료나눔 & 거래</p>
              </div>
            </div>
            <button onclick="openMarketWriteModal()" class="px-3 py-1.5 bg-orange-500 hover:bg-orange-600 text-white rounded-full text-xs font-black shadow-sm flex items-center gap-1 transition-transform active:scale-95">
              <i data-lucide="plus" class="w-3.5 h-3.5"></i>
              <span>나눔/판매</span>
            </button>
          </div>

          <!-- Market Category Filter Pills -->
          <div class="flex gap-1.5 overflow-x-auto pb-1 text-[11px] font-bold">
            <button onclick="filterMarketCategory('all', this)" class="market-tab-btn active px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 whitespace-nowrap">전체 보기</button>
            <button onclick="filterMarketCategory('free', this)" class="market-tab-btn px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 whitespace-nowrap">🎁 100% 무료나눔만</button>
            <button onclick="filterMarketCategory('fit', this)" class="market-tab-btn px-3 py-1.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 whitespace-nowrap">🐶 우리 아이 맞춤 (3.4kg)</button>
            <button onclick="filterMarketCategory('food', this)" class="market-tab-btn px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 whitespace-nowrap">🍗 사료/간식</button>
            <button onclick="filterMarketCategory('cloth', this)" class="market-tab-btn px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 whitespace-nowrap">👕 의류/하네스</button>
            <button onclick="filterMarketCategory('gear', this)" class="market-tab-btn px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 whitespace-nowrap">🚗 유모차/가전</button>
          </div>

          <!-- Market Items Grid / List -->
          <div id="market-items-container" class="space-y-2.5">
            <!-- Dynamic items rendered via JS -->
          </div>
        </div>
"""

if '<!-- 🥕 [PET MARKET]' not in html:
    html = html.replace('<!-- 🏘️ [COMMUNITY]', home_market_section + '\n\n        <!-- 🏘️ [COMMUNITY]')

# Update Nav Bar to 5 clean tabs: [홈, AI검진, 멍당근🥕, 멍냥궁합, 닥터차트]
nav_old = """    <!-- Bottom Navigation Bar (Wayo Style Bright White Bar + Safe Area) -->
    <nav class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white/95 backdrop-blur-md border-t border-slate-200/80 px-2 py-2 flex justify-around z-40 shadow-lg">
      
      <button onclick="switchTab('home')" id="nav-home" class="nav-btn active flex flex-col items-center gap-0.5 text-blue-600 flex-1 py-1">
        <i data-lucide="home" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">홈</span>
      </button>

      <button onclick="switchTab('ai')" id="nav-ai" class="nav-btn flex flex-col items-center gap-0.5 text-slate-400 hover:text-slate-600 flex-1 py-1">
        <i data-lucide="sparkles" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">AI검진</span>
      </button>

      <button onclick="switchTab('compat')" id="nav-compat" class="nav-btn flex flex-col items-center gap-0.5 text-slate-400 hover:text-slate-600 flex-1 py-1">
        <i data-lucide="heart" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">멍냥궁합</span>
      </button>

      <button onclick="switchTab('chart')" id="nav-chart" class="nav-btn flex flex-col items-center gap-0.5 text-slate-400 hover:text-slate-600 flex-1 py-1">
        <i data-lucide="clipboard-list" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">닥터차트</span>
      </button>

      <button onclick="switchTab('settings')" id="nav-settings" class="nav-btn flex flex-col items-center gap-0.5 text-slate-400 hover:text-slate-600 flex-1 py-1">
        <i data-lucide="user" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">내정보</span>
      </button>

    </nav>"""

nav_new = """    <!-- Bottom Navigation Bar (Wayo Style Bright White Bar + Safe Area) -->
    <nav class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white/95 backdrop-blur-md border-t border-slate-200/80 px-1 py-2 flex justify-around z-40 shadow-lg">
      
      <button onclick="switchTab('home')" id="nav-home" class="nav-btn active flex flex-col items-center gap-0.5 text-blue-600 flex-1 py-1">
        <i data-lucide="home" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">홈</span>
      </button>

      <button onclick="switchTab('ai')" id="nav-ai" class="nav-btn flex flex-col items-center gap-0.5 text-slate-400 hover:text-slate-600 flex-1 py-1">
        <i data-lucide="sparkles" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">AI검진</span>
      </button>

      <button onclick="switchTab('market')" id="nav-market" class="nav-btn flex flex-col items-center gap-0.5 text-slate-400 hover:text-slate-600 flex-1 py-1">
        <span class="text-base leading-none">🥕</span>
        <span class="text-[10px] font-bold">멍당근</span>
      </button>

      <button onclick="switchTab('chart')" id="nav-chart" class="nav-btn flex flex-col items-center gap-0.5 text-slate-400 hover:text-slate-600 flex-1 py-1">
        <i data-lucide="clipboard-list" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">닥터차트</span>
      </button>

      <button onclick="switchTab('settings')" id="nav-settings" class="nav-btn flex flex-col items-center gap-0.5 text-slate-400 hover:text-slate-600 flex-1 py-1">
        <i data-lucide="user" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">내정보</span>
      </button>

    </nav>"""

html = html.replace(nav_old, nav_new)

# Add Market Dedicated Tab View (view-market)
market_tab_view = """
      <!-- ================= 7. MARKET TAB (멍당근 전용 화면) ================= -->
      <section id="view-market" class="tab-view hidden p-4 space-y-4">
        <div class="bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-3xl p-5 shadow-md flex items-center justify-between">
          <div>
            <div class="flex items-center gap-1.5">
              <span class="text-xs bg-white/20 px-2.5 py-0.5 rounded-full font-bold">🥕 동네 펫용품 직거래</span>
              <span class="text-xs text-orange-100">역삼1동 안심존</span>
            </div>
            <h3 class="text-xl font-black mt-2">멍당근 나눔 & 장터</h3>
            <p class="text-xs text-orange-100 mt-1">우리 동네 이웃과 따뜻한 나눔을 시작하세요 🐾</p>
          </div>
          <button onclick="openMarketWriteModal()" class="w-12 h-12 rounded-2xl bg-white text-orange-600 flex items-center justify-center text-2xl shadow-lg shrink-0">
            ✏️
          </button>
        </div>

        <!-- Full Market Items Container -->
        <div id="market-full-items-container" class="space-y-3"></div>
      </section>
"""

if 'id="view-market"' not in html:
    html = html.replace('<!-- ================= 5. SETTINGS & PROFILE TAB', market_tab_view + '\n\n      <!-- ================= 5. SETTINGS & PROFILE TAB')

# Add Market Modals (Write Modal & Detail Modal)
market_modals = """
    <!-- ================= Modal: 멍당근 3초 간편 글쓰기 (나눔/판매) ================= -->
    <div id="modal-market-write" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl overflow-y-auto max-h-[90vh]">
        
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🥕</span>
            <div>
              <h3 class="font-black text-base text-slate-900">펫용품 나눔/판매 등록</h3>
              <p class="text-[10px] text-slate-400">사진 올리고 동네 이웃에게 3초 만에 알림</p>
            </div>
          </div>
          <button onclick="closeMarketWriteModal()" class="p-1 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>

        <!-- Photo Upload -->
        <div>
          <label class="font-bold text-slate-700 block mb-1 text-xs">물품 사진 (필수) 📸</label>
          <div class="flex gap-2 items-center">
            <label for="market-photo-input" class="w-20 h-20 rounded-2xl border-2 border-dashed border-orange-300 bg-orange-50/50 flex flex-col items-center justify-center text-orange-600 cursor-pointer hover:bg-orange-100 transition-colors shrink-0">
              <i data-lucide="camera" class="w-6 h-6"></i>
              <span class="text-[10px] font-bold mt-1">사진 추가</span>
            </label>
            <input type="file" id="market-photo-input" accept="image/*" onchange="handleMarketPhoto(event)" class="hidden">
            <div id="market-photo-preview" class="w-20 h-20 rounded-2xl bg-slate-100 border overflow-hidden flex items-center justify-center text-3xl">
              🧸
            </div>
          </div>
        </div>

        <!-- Trade Mode (Free vs Sale) -->
        <div>
          <label class="font-bold text-slate-700 block mb-1 text-xs">거래 방식 선택</label>
          <div class="grid grid-cols-2 gap-2 text-xs font-bold">
            <button type="button" onclick="selectMarketTradeMode('free', this)" class="market-trade-btn py-2.5 rounded-xl border bg-orange-500 text-white active">🎁 무료 나눔 (0원)</button>
            <button type="button" onclick="selectMarketTradeMode('sale', this)" class="market-trade-btn py-2.5 rounded-xl border bg-slate-50 text-slate-700">💰 중고 판매 (가격입력)</button>
          </div>
        </div>

        <!-- Title & Price -->
        <div class="space-y-2 text-xs">
          <div>
            <label class="font-bold text-slate-700 block mb-1">제목</label>
            <input type="text" id="market-input-title" placeholder="예: 3.5kg 소형견 겨울 기모 패딩 나눔해요!" class="w-full p-2.5 rounded-xl border bg-slate-50 font-bold outline-none">
          </div>
          <div id="market-price-box" class="hidden">
            <label class="font-bold text-slate-700 block mb-1">판매 희망 가격 (원)</label>
            <input type="number" id="market-input-price" placeholder="예: 15000" class="w-full p-2.5 rounded-xl border bg-slate-50 font-bold outline-none">
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">카테고리</label>
            <select id="market-input-cat" class="w-full p-2.5 rounded-xl border bg-slate-50 font-bold outline-none">
              <option value="cloth">👕 의류 / 하네스 / 신발</option>
              <option value="food">🍗 사료 / 간식 / 영양제</option>
              <option value="toy">🧸 장난감 / 훈련용품 / 식기</option>
              <option value="gear">🚗 유모차 / 켄넬 / 대형가전</option>
            </select>
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">추천 착용 체중 / 설명</label>
            <textarea id="market-input-desc" rows="2" placeholder="아이 체중(예: 3kg~4kg)이나 깨끗한 상태, 문고리 비대면 나눔 장소를 적어주세요." class="w-full p-2.5 rounded-xl border bg-slate-50 outline-none"></textarea>
          </div>
        </div>

        <button onclick="submitMarketPost()" class="w-full py-3.5 bg-orange-500 hover:bg-orange-600 text-white font-black rounded-2xl text-xs shadow-lg transition-transform active:scale-98">
          동네 이웃에게 나눔/판매 등록하기 ✨
        </button>

      </div>
    </div>

    <!-- ================= Modal: 멍당근 물품 상세 & 1:1 멍채팅 ================= -->
    <div id="modal-market-detail" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-md bg-white h-full sm:h-[85vh] sm:rounded-3xl flex flex-col border border-slate-200 animate-slide-up overflow-hidden text-left shadow-2xl">
        <div class="relative h-60 bg-slate-200 shrink-0">
          <img id="detail-market-img" src="" class="w-full h-full object-cover">
          <button onclick="closeMarketDetailModal()" class="absolute top-3 right-3 p-2 rounded-full bg-black/50 text-white hover:bg-black/70">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
          <div class="absolute bottom-3 left-3 flex gap-1.5">
            <span id="detail-market-type-badge" class="bg-orange-500 text-white font-black text-xs px-2.5 py-0.5 rounded-full shadow">🎁 무료 나눔</span>
            <span class="bg-emerald-600 text-white font-black text-xs px-2.5 py-0.5 rounded-full shadow">세탁/살균 완료</span>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-4">
          <!-- Seller Info & Manner Temp -->
          <div class="flex items-center justify-between border-b border-slate-100 pb-3">
            <div class="flex items-center gap-2.5">
              <div class="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center text-xl shadow-inner">
                🐶
              </div>
              <div>
                <h4 id="detail-seller-name" class="font-black text-xs text-slate-900">역삼 래미안 뽀삐맘</h4>
                <p class="text-[10px] text-slate-400">서울 강남구 역삼1동 • 250m</p>
              </div>
            </div>
            <div class="text-right">
              <span class="text-[10px] text-orange-600 font-bold block">멍매너 온도</span>
              <span class="badge-manner-temp text-xs font-black px-2 py-0.5 rounded-full inline-block">99.2℃ 🔥</span>
            </div>
          </div>

          <!-- Item Details -->
          <div class="space-y-1">
            <h3 id="detail-market-title" class="font-black text-base text-slate-900">3.5kg 소형견 겨울 기모 패딩 나눔해요 🐾</h3>
            <p id="detail-market-price" class="text-xl font-black text-orange-600">0원 (무료나눔)</p>
          </div>

          <!-- Fit Recommendation -->
          <div class="p-3 bg-blue-50 rounded-2xl border border-blue-100 text-xs space-y-1">
            <span class="font-bold text-blue-700 flex items-center gap-1">
              <span>🐶 초코(3.4kg) 맞춤 추천</span>
              <span class="text-[10px] bg-blue-600 text-white px-1.5 rounded">사이즈 딱 맞음</span>
            </span>
            <p id="detail-market-desc" class="text-slate-600 text-[11px] leading-relaxed">
              작년에 사서 2번 입히고 작아져서 깨끗하게 세탁 후 보관 중입니다. 3kg~3.8kg 아이들에게 예쁘게 잘 맞습니다.
            </p>
          </div>

          <!-- Trade Location -->
          <div class="p-3 bg-slate-50 rounded-2xl border border-slate-100 text-xs flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-lg">🚪</span>
              <div>
                <span class="font-bold text-slate-800">문고리 비대면 나눔 가능</span>
                <p class="text-[10px] text-slate-400">역삼 래미안 102동 앞 또는 문고리</p>
              </div>
            </div>
            <span class="text-xs text-blue-600 font-bold">비대면 안심</span>
          </div>

          <!-- Chat & Action Button -->
          <div class="pt-2 flex gap-2">
            <button onclick="startMarketChat()" class="flex-1 py-3.5 bg-orange-500 hover:bg-orange-600 text-white font-black rounded-2xl text-xs flex items-center justify-center gap-1.5 shadow-md">
              <i data-lucide="message-circle" class="w-4 h-4"></i>
              <span>1:1 멍채팅으로 나눔/거래 신청하기</span>
            </button>
          </div>
        </div>
      </div>
    </div>
"""

if 'id="modal-market-write"' not in html:
    html = html.replace('<!-- ================= MODALS ================= -->', '<!-- ================= MODALS ================= -->\n' + market_modals)

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated with complete 멍당근 market ecosystem.")

# 3. Update app.js logic with Market Items, Filtering, Writing, and Detail Chat
with open(app_file, 'r', encoding='utf-8') as f:
    js = f.read()

market_app_logic = """
// ================= 12. 멍당근 (동네 펫용품 나눔 & 중고장터) Engine =================
let marketItems = JSON.parse(localStorage.getItem('petlog_market_items')) || [
  {
    id: 1,
    title: '3.5kg 소형견 겨울 기모 패딩 나눔해요 🐾',
    type: 'free', // 'free' or 'sale'
    price: 0,
    category: 'cloth',
    seller: '역삼 래미안 뽀삐맘',
    distance: '250m (도보 3분)',
    temp: '99.2℃',
    fitWeight: '3.0kg~3.8kg',
    desc: '작년에 사서 2번 입히고 작아져서 깨끗하게 세탁 후 보관 중입니다. 3.4kg 초코 같은 체형에 딱 맞습니다! 문고리 나눔 환영합니다.',
    img: 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=500&auto=format&fit=crop&q=80',
    tags: ['세탁완료', '문고리비대면', '소형견전용']
  },
  {
    id: 2,
    title: '로얄캐닌 인도어 어덜트 소분 1kg 기호성 테스트용 나눔 🍗',
    type: 'free',
    price: 0,
    category: 'food',
    seller: '역삼 센트럴 몽이네',
    distance: '400m (도보 5분)',
    temp: '98.5℃',
    fitWeight: '전견종',
    desc: '대용량 뜯어서 진공 소분해 둔 1kg입니다. 유통기한 2027년 5월까지 넉넉합니다. 사료 기호성 테스트해보실 분 편하게 가져가세요!',
    img: 'https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=500&auto=format&fit=crop&q=80',
    tags: ['미개봉소분', '유통기한넉넉', '기호성테스트']
  },
  {
    id: 3,
    title: '콤비 원터치 접이식 펫 유모차 (개모차 A급) 🚗',
    type: 'sale',
    price: 45000,
    category: 'gear',
    seller: '도곡동 콩이아빠',
    distance: '650m (도보 8분)',
    temp: '97.8℃',
    fitWeight: '최대 10kg',
    desc: '바퀴 부드럽고 가볍습니다. 실사용 5회 미만이라 바퀴 상태 아주 깨끗합니다. 직거래 희망합니다.',
    img: 'https://images.unsplash.com/photo-1541599540903-216a46ca1dc0?w=500&auto=format&fit=crop&q=80',
    tags: ['실사용5회', '상태A급', '직거래']
  },
  {
    id: 4,
    title: '원목 2구 식기 & 노즈워크 플레이 매트 가져가세요 🧸',
    type: 'free',
    price: 0,
    category: 'toy',
    seller: '역삼동 두부맘',
    distance: '320m (도보 4분)',
    temp: '99.0℃',
    fitWeight: '전견종',
    desc: '아이가 다른 식기로 바꿔서 깨끗이 열탕 소독한 원목 식기 나눔합니다. 문고리 걸어둘게요~',
    img: 'https://images.unsplash.com/photo-1535930891776-0c2dfb7fda1a?w=500&auto=format&fit=crop&q=80',
    tags: ['소독완료', '무료나눔', '문고리비대면']
  }
];

let currentMarketFilter = 'all';
let tempMarketUploadedPhoto = null;
let currentSelectedTradeMode = 'free';

function renderMarketItems() {
  const homeContainer = document.getElementById('market-items-container');
  const fullContainer = document.getElementById('market-full-items-container');

  let filtered = marketItems;
  if (currentMarketFilter === 'free') {
    filtered = marketItems.filter(i => i.type === 'free');
  } else if (currentMarketFilter === 'fit') {
    filtered = marketItems.filter(i => i.category === 'cloth' || i.fitWeight.includes('3.'));
  } else if (currentMarketFilter !== 'all') {
    filtered = marketItems.filter(i => i.category === currentMarketFilter);
  }

  const itemsHtml = filtered.map(item => `
    <div onclick="openMarketDetailModal(${item.id})" class="p-3 bg-white rounded-2xl border border-slate-100 hover:border-orange-300 shadow-xs flex gap-3 cursor-pointer transition-all active:scale-99">
      <div class="w-20 h-20 rounded-xl bg-slate-100 overflow-hidden shrink-0 relative">
        <img src="${item.img}" class="w-full h-full object-cover">
        ${item.type === 'free' ? '<span class="absolute top-1 left-1 bg-rose-500 text-white text-[9px] font-black px-1.5 py-0.2 rounded-md shadow">나눔</span>' : ''}
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

  if (homeContainer) homeContainer.innerHTML = itemsHtml;
  if (fullContainer) fullContainer.innerHTML = itemsHtml;
}

window.filterMarketCategory = function(cat, btn) {
  currentMarketFilter = cat;
  document.querySelectorAll('.market-tab-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderMarketItems();
};

window.openMarketWriteModal = function() {
  const modal = document.getElementById('modal-market-write');
  if (modal) {
    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  }
};

window.closeMarketWriteModal = function() {
  const modal = document.getElementById('modal-market-write');
  if (modal) modal.classList.add('hidden');
};

window.handleMarketPhoto = function(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    tempMarketUploadedPhoto = e.target.result;
    const preview = document.getElementById('market-photo-preview');
    if (preview) {
      preview.innerHTML = `<img src="${tempMarketUploadedPhoto}" class="w-full h-full object-cover">`;
    }
  };
  reader.readAsDataURL(file);
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
  const priceInput = document.getElementById('market-input-price').value;

  if (!title) {
    alert('물품 제목을 입력해 주세요!');
    document.getElementById('market-input-title').focus();
    return;
  }

  const newItem = {
    id: Date.now(),
    title: title,
    type: currentSelectedTradeMode,
    price: currentSelectedTradeMode === 'free' ? 0 : parseInt(priceInput || '0'),
    category: cat,
    seller: (currentUser ? currentUser.name : '역삼동 이웃') + ` (${currentPet.name} 보호자)`,
    distance: '내 동네 (방금 전)',
    temp: '99.0℃',
    fitWeight: '맞춤 체형',
    desc: desc || '깨끗하게 보관 중인 물품입니다. 문고리 비대면 나눔 가능합니다.',
    img: tempMarketUploadedPhoto || 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=500&auto=format&fit=crop&q=80',
    tags: ['동네나눔', '문고리비대면']
  };

  marketItems.unshift(newItem);
  localStorage.setItem('petlog_market_items', JSON.stringify(marketItems));
  renderMarketItems();
  closeMarketWriteModal();
  alert(`🎉 [${title}] 나눔/거래 등록이 완료되었습니다!\\n동네 이웃 견주들에게 알림이 발송되었습니다.`);
};

// Market Detail Modal & 1:1 Chat
window.openMarketDetailModal = function(id) {
  const item = marketItems.find(i => i.id === id);
  if (!item) return;

  const modal = document.getElementById('modal-market-detail');
  if (modal) {
    document.getElementById('detail-market-img').src = item.img;
    document.getElementById('detail-seller-name').textContent = item.seller;
    document.getElementById('detail-market-title').textContent = item.title;
    document.getElementById('detail-market-price').textContent = item.type === 'free' ? '0원 (무료나눔)' : item.price.toLocaleString() + '원';
    document.getElementById('detail-market-desc').textContent = item.desc;
    document.getElementById('detail-market-type-badge').textContent = item.type === 'free' ? '🎁 무료 나눔' : '💰 중고 거래';
    
    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  }
};

window.closeMarketDetailModal = function() {
  const modal = document.getElementById('modal-market-detail');
  if (modal) modal.classList.add('hidden');
};

window.startMarketChat = function() {
  alert('💬 [1:1 멍채팅 연결]\\n"안녕하세요! 나눔/거래 문의드립니다. 오늘 저녁 문고리 비대면으로 가능할까요?" 메시지를 보냈습니다.');
};

// Add to DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  renderMarketItems();
});
"""

# Update switchTab titles in app.js
js = js.replace("titles = {", "titles = {\n    market: '멍당근 나눔장터',")

if '// ================= 12. 멍당근' not in js:
    js = js + "\n" + market_app_logic

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js updated with complete 멍당근 Market engine.")
