import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"
style_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\style.css"
app_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\app.js"

# 1. Update style.css with Karrot Orange Warm Palette & Dog Biting Carrot animations
new_css = """/* 멍당근 (MeongDanggeun) - Karrot Pet Market Core Theme */
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800;900&display=swap');

:root {
  --karrot-orange: #ff6f0f;
  --karrot-orange-dark: #e8590c;
  --karrot-orange-light: #fff4e6;
  --karrot-cream: #fff9f5;
  --safe-area-top: env(safe-area-inset-top, 0px);
  --safe-area-bottom: env(safe-area-inset-bottom, 16px);
}

body {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
  -webkit-tap-highlight-color: transparent;
  background-color: #f8fafc;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(253, 186, 116, 0.6);
  border-radius: 4px;
}

/* Karrot Card & Animations */
.karrot-card {
  background: #ffffff;
  border: 1px solid #fed7aa/60;
  box-shadow: 0 4px 18px -2px rgba(251, 146, 60, 0.08);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.karrot-card:active {
  transform: scale(0.985);
}

/* Dog Biting Carrot Animation */
@keyframes biteCarrot {
  0%, 100% { transform: rotate(0deg) scale(1); }
  25% { transform: rotate(-6deg) scale(1.08); }
  75% { transform: rotate(4deg) scale(0.98); }
}
.animate-dog-carrot {
  display: inline-flex;
  align-items: center;
  animation: biteCarrot 3s ease-in-out infinite;
}

/* Floating Write Button (FAB) */
.fab-write-btn {
  background: linear-gradient(135deg, #ff6f0f, #ff8c42);
  box-shadow: 0 6px 20px rgba(255, 111, 15, 0.4);
}

/* Category Filter Active */
.category-filter-btn.active {
  background-color: #ff6f0f !important;
  color: #ffffff !important;
  border-color: #ff6f0f !important;
  font-weight: 800;
  box-shadow: 0 3px 10px rgba(255, 111, 15, 0.25);
}

/* Manner Temperature Gradient */
.manner-badge {
  background: linear-gradient(135deg, #ff6f0f, #e8590c);
  color: #ffffff;
}

/* Leaflet Map & Markers */
.leaflet-container {
  font-family: 'Pretendard', sans-serif !important;
}
.custom-user-marker, .custom-place-marker, .custom-walk-marker, .custom-poop-marker {
  border: none !important;
  background: transparent !important;
}

/* Mobile Safe Area Inset Support (Android 3-Button & iOS) */
#app-container {
  padding-bottom: calc(5.2rem + env(safe-area-inset-bottom, 22px)) !important;
}

nav.fixed.bottom-0 {
  padding-bottom: calc(0.6rem + env(safe-area-inset-bottom, 18px)) !important;
  padding-left: max(0.5rem, env(safe-area-inset-left, 0px)) !important;
  padding-right: max(0.5rem, env(safe-area-inset-right, 0px)) !important;
}

#modal-market-write > div,
#modal-market-detail > div,
#modal-pet-profile > div,
#modal-sitter-detail > div,
#modal-live-walk-gps > div,
#modal-auth > div,
#modal-trial-limit > div {
  margin-bottom: calc(env(safe-area-inset-bottom, 16px) + 0.5rem);
}
"""

with open(style_file, 'w', encoding='utf-8') as f:
    f.write(new_css)

print("style.css updated with 멍당근 Karrot theme.")

# 2. Build 멍당근 Centric index.html
mungdanggeun_html = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>멍당근 - 동네 펫용품 나눔장터 & 1초 AI 펫케어</title>
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            karrot: {
              50: '#fff9f5',
              100: '#fff4e6',
              200: '#ffe8cc',
              500: '#ff6f0f',
              600: '#e8590c',
              700: '#d9480f',
            }
          },
          borderRadius: {
            '3xl': '24px',
            '4xl': '32px',
          }
        }
      }
    }
  </script>

  <!-- Lucide Icons CDN -->
  <script src="https://unpkg.com/lucide@latest"></script>
  
  <!-- html2pdf.js for Doctor Chart Export -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>

  <!-- Leaflet Map CSS/JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <!-- Kakao Map SDK -->
  <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey=a0a8a6c45e622ea183ef6fc5ae3f3e5d&libraries=services&autoload=false"></script>

  <!-- Google Identity Services -->
  <script src="https://accounts.google.com/gsi/client" async defer></script>

  <!-- Custom Styles -->
  <link rel="stylesheet" href="style.css">
</head>
<body class="bg-slate-100 text-slate-800 flex justify-center min-h-screen antialiased select-none">

  <!-- Mobile Frame Container -->
  <div id="app-container" class="w-full max-w-md bg-white min-h-screen shadow-xl relative flex flex-col pb-28 overflow-x-hidden border-x border-slate-200">
    
    <!-- Top Status Bar Simulation -->
    <div class="sticky top-0 z-40 bg-white/95 backdrop-blur-md px-5 py-2 flex items-center justify-between border-b border-slate-100 text-xs text-slate-400">
      <div class="font-bold flex items-center gap-1.5 text-slate-800">
        <span id="current-time">09:19</span>
        <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
      </div>
      <div class="flex items-center gap-2">
        <i data-lucide="wifi" class="w-3.5 h-3.5 text-slate-600"></i>
        <i data-lucide="signal" class="w-3.5 h-3.5 text-slate-600"></i>
        <div class="flex items-center gap-0.5 font-bold text-[10px] text-slate-700">
          <i data-lucide="battery" class="w-4 h-4 text-emerald-500"></i>
          <span>90%</span>
        </div>
      </div>
    </div>

    <!-- App Header (멍당근 Biting Carrot Mascot & Location Branding) -->
    <header class="px-4 py-3 flex items-center justify-between bg-white sticky top-8 z-30 border-b border-orange-100 shadow-xs">
      <div class="flex items-center gap-2">
        <!-- Mascot: Puppy Biting Carrot 🐶🥕 -->
        <div onclick="switchTab('home')" class="cursor-pointer flex items-center gap-1.5">
          <div class="animate-dog-carrot text-2xl relative">
            <span>🐶</span>
            <span class="text-lg -ml-2 -mt-1 transform -rotate-12">🥕</span>
          </div>
          <div>
            <h1 class="text-xl font-black tracking-tight text-orange-600 leading-none">멍당근</h1>
            <div class="flex items-center gap-0.5 mt-0.5">
              <span class="text-[10px] font-black text-slate-700">서울 강남구 역삼1동</span>
              <i data-lucide="chevron-down" class="w-3 h-3 text-slate-400"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- Header Right: Mode Switcher & Login -->
      <div class="flex items-center gap-1.5">
        <!-- Dual Mode Switcher (견주 ↔ 펫시터) -->
        <div class="flex bg-orange-50 p-0.5 rounded-full text-[10px] font-black border border-orange-200">
          <button id="btn-mode-owner" onclick="switchAppMode('owner')" class="px-2 py-0.5 rounded-full bg-orange-500 text-white shadow-xs transition-all">🐕 견주</button>
          <button id="btn-mode-sitter" onclick="switchAppMode('sitter')" class="px-2 py-0.5 rounded-full text-slate-500 hover:text-slate-800 transition-all">🏠 펫시터</button>
        </div>

        <!-- Social Auth Login Button -->
        <button id="btn-header-auth" onclick="openAuthModal()" class="flex items-center gap-1 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-full text-xs font-bold border border-slate-200 transition-transform active:scale-95">
          <i data-lucide="log-in" class="w-3 h-3 text-orange-500"></i>
          <span id="header-auth-label">로그인</span>
        </button>
      </div>
    </header>

    <!-- Main Content Container -->
    <main id="tab-content" class="flex-1 overflow-y-auto">

      <!-- ================= 1. HOME TAB (멍당근 동네 나눔 & 직거래 메인 허브) ================= -->
      <section id="view-home" class="tab-view space-y-4 px-4 pt-3">
        
        <!-- My Pet Custom Welcome & Profile Box -->
        <div class="karrot-card rounded-3xl p-4 bg-gradient-to-r from-orange-50 via-amber-50/50 to-orange-50/80 border border-orange-200/80 shadow-xs">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <!-- Clickable Pet Avatar -->
              <div onclick="openPetProfileModal()" class="relative cursor-pointer group">
                <div id="home-pet-avatar" class="w-14 h-14 rounded-2xl bg-white border-2 border-orange-400 shadow-sm flex items-center justify-center text-3xl overflow-hidden group-hover:scale-105 transition-transform">
                  🐕
                </div>
                <div class="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-orange-500 text-white flex items-center justify-center text-[9px] shadow border border-white">
                  🥕
                </div>
              </div>

              <!-- Dynamic Name & Breed Info -->
              <div class="space-y-0.5">
                <div class="flex items-center gap-1.5">
                  <span class="text-[9px] px-1.5 py-0.2 rounded-full bg-orange-500 text-white font-black">내 반려동물</span>
                  <span id="home-pet-subtext" class="text-xs font-bold text-slate-500">말티즈 • 3세 • 3.4kg</span>
                </div>
                <h2 id="home-welcome-title" class="text-base font-black text-slate-900 leading-snug">
                  <span id="home-pet-name" class="text-orange-600">초코</span>네 동네 나눔장터~ 🥕
                </h2>
              </div>
            </div>

            <!-- Profile Edit Trigger Button -->
            <button onclick="openPetProfileModal()" class="px-2.5 py-1.5 rounded-xl bg-white hover:bg-orange-50 text-orange-600 border border-orange-200 text-xs font-bold shadow-xs shrink-0 flex items-center gap-1 transition-transform active:scale-95">
              <i data-lucide="edit-3" class="w-3 h-3"></i>
              <span>아이 변경</span>
            </button>
          </div>
        </div>

        <!-- 4-Icon Companion Care Hub (AI검진 / 펫시터 / 닥터차트 / 멍냥궁합) -->
        <div class="bg-white rounded-3xl p-3.5 border border-slate-100 shadow-xs">
          <div class="grid grid-cols-4 gap-2 text-center">
            
            <div onclick="switchTab('ai')" class="p-2 rounded-2xl hover:bg-blue-50 cursor-pointer transition-colors group">
              <div class="w-11 h-11 rounded-2xl bg-blue-50 group-hover:bg-blue-100 mx-auto flex items-center justify-center text-2xl mb-1 shadow-xs">
                📸
              </div>
              <span class="text-xs font-black text-slate-800 block">AI 검진</span>
              <span class="text-[9px] text-blue-600 font-bold">1초 판별</span>
            </div>

            <div onclick="switchTab('sitter-explore')" class="p-2 rounded-2xl hover:bg-emerald-50 cursor-pointer transition-colors group">
              <div class="w-11 h-11 rounded-2xl bg-emerald-50 group-hover:bg-emerald-100 mx-auto flex items-center justify-center text-2xl mb-1 shadow-xs">
                🏡
              </div>
              <span class="text-xs font-black text-slate-800 block">동네 펫시터</span>
              <span class="text-[9px] text-emerald-600 font-bold">가정집 돌봄</span>
            </div>

            <div onclick="switchTab('chart')" class="p-2 rounded-2xl hover:bg-indigo-50 cursor-pointer transition-colors group">
              <div class="w-11 h-11 rounded-2xl bg-indigo-50 group-hover:bg-indigo-100 mx-auto flex items-center justify-center text-2xl mb-1 shadow-xs">
                📋
              </div>
              <span class="text-xs font-black text-slate-800 block">닥터 차트</span>
              <span class="text-[9px] text-indigo-600 font-bold">원장님 PDF</span>
            </div>

            <div onclick="switchTab('compat')" class="p-2 rounded-2xl hover:bg-rose-50 cursor-pointer transition-colors group">
              <div class="w-11 h-11 rounded-2xl bg-rose-50 group-hover:bg-rose-100 mx-auto flex items-center justify-center text-2xl mb-1 shadow-xs">
                💖
              </div>
              <span class="text-xs font-black text-slate-800 block">멍냥 궁합</span>
              <span class="text-[9px] text-rose-600 font-bold">음성 번역기</span>
            </div>

          </div>
        </div>

        <!-- 🥕 [CORE 1] 멍당근 실시간 동네 나눔 & 득템 피드 -->
        <div class="space-y-3 pt-1">
          <div class="flex items-center justify-between px-1">
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-xl bg-orange-500 text-white flex items-center justify-center text-sm font-black shadow-xs">
                🥕
              </div>
              <div>
                <h3 class="text-base font-black text-slate-900">역삼1동 펫용품 나눔장터</h3>
                <p class="text-[11px] text-slate-400">우리 동네 이웃들의 따뜻한 무료나눔 & 안심 직거래</p>
              </div>
            </div>
            <button onclick="openMarketWriteModal()" class="px-3 py-1.5 bg-orange-500 hover:bg-orange-600 text-white rounded-full text-xs font-black shadow-sm flex items-center gap-1 transition-transform active:scale-95">
              <i data-lucide="plus" class="w-3.5 h-3.5"></i>
              <span>나눔/판매</span>
            </button>
          </div>

          <!-- Category Filter Pills -->
          <div class="flex gap-1.5 overflow-x-auto pb-1 text-[11px] font-bold">
            <button onclick="filterMarketCategory('all', this)" class="category-filter-btn active px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 whitespace-nowrap">전체 보기</button>
            <button onclick="filterMarketCategory('free', this)" class="category-filter-btn px-3 py-1.5 rounded-full bg-rose-50 text-rose-600 border border-rose-200 whitespace-nowrap">🎁 100% 무료나눔만</button>
            <button onclick="filterMarketCategory('fit', this)" class="category-filter-btn px-3 py-1.5 rounded-full bg-orange-50 text-orange-700 border border-orange-200 whitespace-nowrap">🐶 초코 맞춤 (3.4kg)</button>
            <button onclick="filterMarketCategory('food', this)" class="category-filter-btn px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 whitespace-nowrap">🍗 사료/간식</button>
            <button onclick="filterMarketCategory('cloth', this)" class="category-filter-btn px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 whitespace-nowrap">👕 의류/하네스</button>
            <button onclick="filterMarketCategory('gear', this)" class="category-filter-btn px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 whitespace-nowrap">🚗 유모차/켄넬</button>
          </div>

          <!-- Market Items Grid / List -->
          <div id="market-items-container" class="space-y-2.5">
            <!-- Rendered dynamically -->
          </div>
        </div>

        <!-- 🎥 실시간 10초 멍스토리 릴스 바 -->
        <div class="karrot-card rounded-3xl p-3.5 bg-gradient-to-r from-orange-50/60 via-pink-50/40 to-purple-50/60 border border-orange-100 shadow-xs">
          <div class="flex items-center justify-between mb-2 px-1">
            <div class="flex items-center gap-1.5">
              <span class="text-xs font-black text-slate-900">🎥 실시간 LIVE 10초 멍스토리</span>
              <span class="text-[9px] bg-rose-500 text-white font-black px-1.5 py-0.2 rounded-full animate-pulse">LIVE</span>
            </div>
            <span class="text-[10px] text-slate-400 font-semibold">인스타 스토리 연동</span>
          </div>
          <div class="flex gap-3 overflow-x-auto py-1">
            <div onclick="openShortStoryModal('초코', '김은지 펫시터', '장난감 터그놀이 삼매경 🧸', '🐕')" class="flex flex-col items-center gap-1 cursor-pointer shrink-0">
              <div class="story-ring">
                <div class="w-13 h-13 rounded-full bg-white p-0.5">
                  <div class="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center text-2xl shadow-inner">🐕</div>
                </div>
              </div>
              <span class="text-[10px] font-bold text-slate-700">초코 (놀이중)</span>
            </div>
            <div onclick="openShortStoryModal('뽀삐', '박서준 훈련사', '역삼공원 쾌변 산책 똥꼬발랄 🐾', '🐩')" class="flex flex-col items-center gap-1 cursor-pointer shrink-0">
              <div class="story-ring">
                <div class="w-13 h-13 rounded-full bg-white p-0.5">
                  <div class="w-12 h-12 rounded-full bg-rose-100 flex items-center justify-center text-2xl shadow-inner">🐩</div>
                </div>
              </div>
              <span class="text-[10px] font-bold text-slate-700">뽀삐 (산책중)</span>
            </div>
            <div onclick="openShortStoryModal('루나', '정다은 펫시터', '츄르 먹방 & 꿀잠 골골송 💤', '🐈')" class="flex flex-col items-center gap-1 cursor-pointer shrink-0">
              <div class="story-ring">
                <div class="w-13 h-13 rounded-full bg-white p-0.5">
                  <div class="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center text-2xl shadow-inner">🐈</div>
                </div>
              </div>
              <span class="text-[10px] font-bold text-slate-700">루나 (식사중)</span>
            </div>
          </div>
        </div>

        <!-- 🛡️ 펫로그 안심 케어 보증제 -->
        <div class="bg-gradient-to-r from-emerald-500/15 via-teal-500/10 to-orange-500/15 border border-emerald-500/30 rounded-3xl p-4 flex items-center justify-between shadow-xs">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-2xl bg-emerald-500 text-white flex items-center justify-center text-xl shadow">
              🛡️
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <span class="text-xs font-black text-emerald-800">멍당근 안심 100% 보증제</span>
                <span class="text-[9px] bg-emerald-600 text-white font-black px-1.5 py-0.2 rounded-full">안심직거래</span>
              </div>
              <p class="text-[11px] text-slate-600 mt-0.5">동네 나눔/거래 사기 방지 & 돌봄 사고 시 최대 500만원 지원</p>
            </div>
          </div>
        </div>

      </section>

      <!-- ================= 2. AI SCANNER TAB ================= -->
      <section id="view-ai" class="tab-view hidden p-4 space-y-4">
        <div class="bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-3xl p-5 shadow-md">
          <span class="text-xs bg-white/20 px-2.5 py-0.5 rounded-full font-bold">✨ Gemini 비전 AI 엔진</span>
          <h3 class="text-xl font-black mt-2">📸 AI 1초 사진 건강 스캐너</h3>
          <p class="text-xs text-blue-100 mt-1">이상 부위(피부 붉은기, 귀 안쪽, 대변, 눈물 자국)를 촬영해 주세요.</p>
        </div>

        <div id="ai-dropzone" onclick="triggerAIScan()" class="border-2 border-dashed border-blue-300 hover:border-blue-500 rounded-3xl p-6 text-center cursor-pointer bg-blue-50/40 hover:bg-blue-50/70 transition-all space-y-2">
          <div class="w-16 h-16 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-3xl mx-auto shadow-inner">
            📷
          </div>
          <div>
            <p class="text-sm font-black text-slate-800">터치하여 사진 촬영 / 갤러리 업로드</p>
            <p class="text-xs text-slate-400 mt-0.5">JPG, PNG (비회원 1회 무료 / 회원 무제한 무료)</p>
          </div>
        </div>

        <div id="ai-result-box" class="hidden karrot-card rounded-3xl p-5 space-y-3 border border-emerald-200 bg-emerald-50/30 animate-slide-up">
          <div class="flex items-center justify-between border-b border-emerald-200/60 pb-2">
            <span class="text-emerald-600 font-black text-sm">✅ AI 비전 정밀 분석 완료</span>
            <span class="text-xs font-bold text-slate-500">신뢰도 96.4%</span>
          </div>
          <div class="p-3 bg-white rounded-2xl border border-emerald-100 shadow-xs space-y-1 text-xs">
            <div class="flex justify-between items-center font-bold">
              <span class="text-slate-800">🔍 의심 소견</span>
              <span class="text-rose-600 font-black">지루성 피부염 88%</span>
            </div>
            <p class="text-slate-600">피부 표면의 경미한 발적이 관찰됩니다. 저자극 샴푸 관리와 습도 조절을 권장합니다.</p>
          </div>
          <button onclick="addAIResultToChart()" class="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl shadow-xs text-xs flex items-center justify-center gap-1.5">
            <i data-lucide="plus-circle" class="w-4 h-4"></i>
            <span>이 분석 결과를 닥터 차트에 자동 기록하기</span>
          </button>
        </div>
      </section>

      <!-- ================= 3. SITTER EXPLORE TAB ================= -->
      <section id="view-sitter-explore" class="tab-view hidden p-4 space-y-4">
        <div class="bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-3xl p-5 shadow-md flex items-center justify-between">
          <div>
            <span class="text-xs bg-white/20 px-2.5 py-0.5 rounded-full font-bold">🏡 동네 펫시터</span>
            <h3 class="text-xl font-black mt-2">가정집 안심 돌봄</h3>
            <p class="text-xs text-emerald-100 mt-1">우리 동네 검증된 펫시터와 1:1 매칭</p>
          </div>
          <button onclick="openSitterRegisterModal()" class="px-3 py-2 bg-white text-emerald-700 rounded-2xl text-xs font-black shadow">
            펫시터 지원
          </button>
        </div>

        <!-- Sitter List -->
        <div class="space-y-3">
          <div class="karrot-card rounded-3xl overflow-hidden border border-slate-100 shadow-xs">
            <div class="relative h-44 bg-slate-200 overflow-hidden cursor-pointer" onclick="openSitterDetailModal(1)">
              <img src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&auto=format&fit=crop&q=80" class="w-full h-full object-cover">
              <div class="absolute top-3 left-3 flex gap-1.5">
                <span class="bg-blue-600 text-white font-black text-[10px] px-2.5 py-0.5 rounded-full shadow">단독 케어</span>
                <span class="bg-emerald-600 text-white font-black text-[10px] px-2.5 py-0.5 rounded-full shadow">24시 상주</span>
              </div>
            </div>
            <div class="p-4 space-y-2.5">
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="font-black text-sm text-slate-900">김은지 펫시터 ⭐ 4.98</h4>
                  <p class="text-[11px] text-slate-500">서울 강남구 역삼동 • 도보 350m</p>
                </div>
                <p class="text-base font-black text-slate-900">71,600원 <span class="text-xs text-slate-400">/ 1박</span></p>
              </div>
              <div class="flex gap-2 pt-1">
                <button onclick="openLiveWalkGpsModal('초코', '김은지 펫시터')" class="flex-1 py-2.5 bg-slate-100 font-bold rounded-2xl text-xs">
                  산책 LIVE GPS
                </button>
                <button onclick="openSitterDetailModal(1)" class="flex-1 py-2.5 bg-emerald-600 text-white font-black rounded-2xl text-xs">
                  1:1 돌봄 예약
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= 4. COMPATIBILITY & MBTI TAB ================= -->
      <section id="view-compat" class="tab-view hidden p-4 space-y-4">
        <div class="bg-gradient-to-r from-rose-500 to-orange-500 text-white rounded-3xl p-5 shadow-md">
          <span class="text-xs bg-white/20 px-2.5 py-0.5 rounded-full font-bold">💖 멍냥 케미 분석실</span>
          <h3 class="text-xl font-black mt-2">반려견 성향 MBTI & 음성 번역</h3>
          <p class="text-xs text-rose-100 mt-1">우리 아이의 숨겨진 마음과 친구 댕댕이와의 궁합을 확인하세요!</p>
        </div>

        <div class="karrot-card rounded-3xl p-5 space-y-3">
          <h4 class="font-black text-sm text-slate-800">🎙️ 멍냥 음성/울음소리 AI 번역기</h4>
          <button id="btn-voice-record" onclick="simulateVoiceAnalysis()" class="w-full py-3 bg-rose-50 hover:bg-rose-100 text-rose-600 font-bold rounded-2xl border border-rose-200 text-xs flex items-center justify-center gap-2">
            <span>🎙️ 터치하여 5초간 소리 듣기</span>
          </button>
          <div id="voice-analysis-result" class="hidden p-3 bg-rose-50/50 rounded-2xl border border-rose-100 text-xs space-y-1">
            <p class="font-bold text-rose-700">🐾 AI 번역 결과: "지금 당장 산책 나가고 싶어요! 🐾"</p>
          </div>
        </div>

        <div class="karrot-card rounded-3xl p-5 space-y-3">
          <h4 class="font-black text-sm text-slate-800">💕 친구 댕댕이와의 바이럴 궁합 테스트</h4>
          <button onclick="openCompatibilityModal()" class="w-full py-3 bg-gradient-to-r from-rose-500 to-orange-500 text-white font-black rounded-2xl text-xs">
            우리 초코와 친구 궁합 측정하기
          </button>
        </div>
      </section>

      <!-- ================= 5. DOCTOR CHART TAB ================= -->
      <section id="view-chart" class="tab-view hidden p-4 space-y-4">
        <div class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-3xl p-5 shadow-md">
          <span class="text-xs bg-white/20 px-2.5 py-0.5 rounded-full font-bold">🩺 동물병원 원장님 전송 차트</span>
          <h3 class="text-xl font-black mt-2">일일 V-체크 건강 일기</h3>
          <p class="text-xs text-blue-100 mt-1">오늘의 식욕, 배변, 증상을 기록하고 1초 PDF로 전송하세요.</p>
        </div>

        <div class="karrot-card rounded-3xl p-5 space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-black text-slate-800">📅 기록 일자</span>
            <input type="date" id="chart-date-input" class="text-xs p-1.5 rounded-xl border border-slate-200 font-bold bg-slate-50">
          </div>
          <div class="space-y-1.5">
            <span class="text-xs font-bold text-slate-600">🍖 식욕 상태</span>
            <div class="grid grid-cols-4 gap-1.5 text-xs">
              <button onclick="selectCheck(this, 'appetite', '매우좋음')" class="check-btn py-2 rounded-xl text-center">매우좋음</button>
              <button onclick="selectCheck(this, 'appetite', '정상')" class="check-btn active py-2 rounded-xl text-center">정상</button>
              <button onclick="selectCheck(this, 'appetite', '약간감소')" class="check-btn py-2 rounded-xl text-center">약간감소</button>
              <button onclick="selectCheck(this, 'appetite', '거의안먹음')" class="check-btn py-2 rounded-xl text-center">안먹음</button>
            </div>
          </div>
          <div class="space-y-1.5">
            <span class="text-xs font-bold text-slate-600">💩 대변 상태</span>
            <div class="grid grid-cols-4 gap-1.5 text-xs">
              <button onclick="selectCheck(this, 'stool', '정상변')" class="check-btn active py-2 rounded-xl text-center">정상변</button>
              <button onclick="selectCheck(this, 'stool', '묽은변')" class="check-btn py-2 rounded-xl text-center">묽은변</button>
              <button onclick="selectCheck(this, 'stool', '설사')" class="check-btn py-2 rounded-xl text-center">설사</button>
              <button onclick="selectCheck(this, 'stool', '혈변/점액')" class="check-btn py-2 rounded-xl text-center">혈변</button>
            </div>
          </div>
          <div class="space-y-1.5">
            <span class="text-xs font-bold text-slate-600">📝 특이사항 메모</span>
            <input type="text" id="chart-memo-input" placeholder="산책 시간, 약 복용 상태 등을 기록하세요" class="w-full text-xs p-3 rounded-2xl border border-slate-200 bg-slate-50">
          </div>
          <div class="pt-2 flex gap-2">
            <button onclick="saveHealthLog()" class="flex-1 py-3 bg-blue-600 text-white font-black rounded-2xl text-xs">
              오늘 기록 저장하기
            </button>
            <button onclick="exportDoctorChartPDF()" class="px-4 py-3 bg-slate-900 text-white font-bold rounded-2xl text-xs">
              PDF 출력
            </button>
          </div>
        </div>

        <div class="space-y-2">
          <span class="text-xs font-black text-slate-800 px-1">📋 최근 기록 내역</span>
          <div id="chart-history-list" class="space-y-2"></div>
        </div>
      </section>

      <!-- ================= 6. SITTER DASHBOARD (펫시터 파트너 센터) ================= -->
      <section id="view-sitter-dashboard" class="tab-view hidden p-4 space-y-4">
        <div class="bg-gradient-to-r from-slate-900 to-orange-950 text-white rounded-3xl p-5 shadow-lg relative overflow-hidden">
          <span class="text-xs bg-orange-500 text-white font-black px-2.5 py-0.5 rounded-full">
            🏠 펫시터 파트너 센터
          </span>
          <div class="mt-3">
            <span class="text-xs text-slate-300">이번 달 누적 돌봄 수익</span>
            <div class="flex items-baseline gap-1.5 mt-0.5">
              <h3 class="text-3xl font-black text-orange-400">1,450,000</h3>
              <span class="text-sm font-bold text-white">원</span>
            </div>
          </div>
        </div>

        <div class="karrot-card rounded-3xl p-5 space-y-3">
          <h4 class="font-black text-sm text-slate-900">🐾 실시간 LIVE 돌봄 관제 도구</h4>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <button onclick="openLiveWalkGpsModal('초코', '김은지 펫시터')" class="p-3 bg-orange-50 rounded-2xl border border-orange-200 flex flex-col items-center gap-1.5">
              <span class="text-2xl">📍</span>
              <span class="font-black text-slate-800">산책 LIVE GPS</span>
            </button>
            <button onclick="openShortStoryModal('초코', '김은지 펫시터', '신나는 터그놀이 🧸', '🐕')" class="p-3 bg-pink-50 rounded-2xl border border-pink-200 flex flex-col items-center gap-1.5">
              <span class="text-2xl">🎥</span>
              <span class="font-black text-slate-800">10초 멍스토리</span>
            </button>
          </div>
          <button onclick="syncSitterLogToDoctorChart('초코')" class="w-full py-3 bg-emerald-600 text-white font-black rounded-2xl text-xs">
            돌봄 일지 $\rightarrow$ 견주 닥터 차트에 자동 동기화
          </button>
        </div>
      </section>

      <!-- ================= 7. SETTINGS & PROFILE TAB ================= -->
      <section id="view-settings" class="tab-view hidden p-4 space-y-3">
        <div id="settings-user-box" class="bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-100 rounded-3xl p-5 shadow-xs">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div id="user-avatar-badge" class="w-14 h-14 rounded-full bg-orange-500 text-white flex items-center justify-center text-2xl font-bold shadow-md overflow-hidden">
                🐶
              </div>
              <div>
                <div class="flex items-center gap-1.5">
                  <span id="user-display-name" class="font-black text-base text-slate-900">게스트 보호자님</span>
                  <span id="user-provider-badge" class="text-[10px] px-2 py-0.5 rounded-full bg-slate-200 text-slate-700 font-bold">비회원</span>
                </div>
                <p id="user-email-text" class="text-xs text-slate-500 mt-0.5">로그인하고 나눔/차트 클라우드 동기화</p>
              </div>
            </div>
            <button id="btn-settings-auth" onclick="openAuthModal()" class="px-3.5 py-2 rounded-2xl bg-orange-500 text-white text-xs font-black shadow-xs">
              로그인
            </button>
          </div>
        </div>

        <div class="karrot-card rounded-3xl p-2 divide-y divide-slate-100 text-sm">
          <button onclick="openPetProfileModal()" class="w-full flex items-center justify-between p-3.5 hover:bg-slate-50 rounded-2xl">
            <div class="flex items-center gap-3">
              <span class="text-lg">🐶</span>
              <span class="font-bold text-slate-800">반려동물 정보 & 테마 변경</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
          </button>
          <button onclick="openMapModal()" class="w-full flex items-center justify-between p-3.5 hover:bg-slate-50 rounded-2xl">
            <div class="flex items-center gap-3">
              <span class="text-lg">🗺️</span>
              <span class="font-bold text-slate-800">카카오 공식 1km 펫지도</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
          </button>
        </div>
      </section>

    </main>

    <!-- Bottom Navigation Bar (Karrot Market Style 5 Tabs + Center FAB) -->
    <nav class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white/95 backdrop-blur-md border-t border-slate-200 px-1 py-2 flex justify-around z-40 shadow-lg">
      
      <button onclick="switchTab('home')" id="nav-home" class="nav-btn active flex flex-col items-center gap-0.5 text-orange-500 flex-1 py-1">
        <span class="text-base leading-none">🥕</span>
        <span class="text-[10px] font-bold">멍당근</span>
      </button>

      <button onclick="switchTab('ai')" id="nav-ai" class="nav-btn flex flex-col items-center gap-0.5 text-slate-400 hover:text-slate-600 flex-1 py-1">
        <i data-lucide="sparkles" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">AI검진</span>
      </button>

      <!-- Center FAB: 3-Second Quick Post -->
      <button onclick="openMarketWriteModal()" class="flex flex-col items-center -mt-5 flex-1 group">
        <div class="w-12 h-12 rounded-full fab-write-btn text-white flex items-center justify-center text-xl shadow-lg transform group-hover:scale-110 transition-transform">
          ✏️
        </div>
        <span class="text-[10px] font-black text-orange-600 mt-0.5">나눔/판매</span>
      </button>

      <button onclick="switchTab('sitter-explore')" id="nav-sitter-explore" class="nav-btn flex flex-col items-center gap-0.5 text-slate-400 hover:text-slate-600 flex-1 py-1">
        <i data-lucide="home" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">펫시터</span>
      </button>

      <button onclick="switchTab('settings')" id="nav-settings" class="nav-btn flex flex-col items-center gap-0.5 text-slate-400 hover:text-slate-600 flex-1 py-1">
        <i data-lucide="user" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">내정보</span>
      </button>

    </nav>

    <!-- ================= MODALS ================= -->

    <!-- Modal: 멍당근 3초 간편 글쓰기 (나눔/판매) -->
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

        <div>
          <label class="font-bold text-slate-700 block mb-1 text-xs">거래 방식 선택</label>
          <div class="grid grid-cols-2 gap-2 text-xs font-bold">
            <button type="button" onclick="selectMarketTradeMode('free', this)" class="market-trade-btn py-2.5 rounded-xl border bg-orange-500 text-white active">🎁 무료 나눔 (0원)</button>
            <button type="button" onclick="selectMarketTradeMode('sale', this)" class="market-trade-btn py-2.5 rounded-xl border bg-slate-50 text-slate-700">💰 중고 판매 (가격입력)</button>
          </div>
        </div>

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

    <!-- Modal: 멍당근 물품 상세 & 1:1 멍채팅 -->
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
          <div class="flex items-center justify-between border-b border-slate-100 pb-3">
            <div class="flex items-center gap-2.5">
              <div class="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center text-xl shadow-inner">🐶</div>
              <div>
                <h4 id="detail-seller-name" class="font-black text-xs text-slate-900">역삼 래미안 뽀삐맘</h4>
                <p class="text-[10px] text-slate-400">서울 강남구 역삼1동 • 250m</p>
              </div>
            </div>
            <div class="text-right">
              <span class="text-[10px] text-orange-600 font-bold block">멍매너 온도</span>
              <span class="manner-badge text-xs font-black px-2 py-0.5 rounded-full inline-block">99.2℃ 🔥</span>
            </div>
          </div>

          <div class="space-y-1">
            <h3 id="detail-market-title" class="font-black text-base text-slate-900">3.5kg 소형견 겨울 기모 패딩 나눔해요 🐾</h3>
            <p id="detail-market-price" class="text-xl font-black text-orange-600">0원 (무료나눔)</p>
          </div>

          <div class="p-3 bg-orange-50 rounded-2xl border border-orange-100 text-xs space-y-1">
            <span class="font-bold text-orange-700 flex items-center gap-1">
              <span>🐶 초코(3.4kg) 맞춤 추천</span>
              <span class="text-[10px] bg-orange-500 text-white px-1.5 rounded">사이즈 딱 맞음</span>
            </span>
            <p id="detail-market-desc" class="text-slate-600 text-[11px] leading-relaxed">
              작년에 사서 2번 입히고 작아져서 깨끗하게 세탁 후 보관 중입니다. 3.4kg 아이들에게 잘 맞습니다.
            </p>
          </div>

          <div class="pt-2 flex gap-2">
            <button onclick="startMarketChat()" class="flex-1 py-3.5 bg-orange-500 hover:bg-orange-600 text-white font-black rounded-2xl text-xs flex items-center justify-center gap-1.5 shadow-md">
              <i data-lucide="message-circle" class="w-4 h-4"></i>
              <span>1:1 멍채팅으로 나눔/거래 신청하기</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Pet Profile Registration & Customizer -->
    <div id="modal-pet-profile" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl overflow-y-auto max-h-[90vh]">
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🐶</span>
            <div>
              <h3 class="font-black text-base text-slate-900">내 반려동물 등록 & 맞춤 설정</h3>
              <p class="text-[10px] text-slate-400">사진과 이름을 등록하면 내 앱으로 커스텀됩니다</p>
            </div>
          </div>
          <button onclick="closePetProfileModal()" class="p-1 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>

        <div class="text-center space-y-2 py-1">
          <div class="relative w-20 h-20 mx-auto">
            <div id="modal-preview-avatar" class="w-20 h-20 rounded-3xl bg-orange-50 border-2 border-orange-400 flex items-center justify-center text-4xl shadow-inner overflow-hidden">
              🐕
            </div>
            <label for="pet-photo-upload" class="absolute -bottom-1 -right-1 p-2 rounded-full bg-orange-500 text-white shadow-lg cursor-pointer hover:bg-orange-600 transition-transform active:scale-90">
              <i data-lucide="camera" class="w-4 h-4"></i>
            </label>
            <input type="file" id="pet-photo-upload" accept="image/*" onchange="handlePetPhotoUpload(event)" class="hidden">
          </div>
          <p class="text-[11px] text-slate-500">카메라를 눌러 <strong>실제 갤러리 사진</strong>을 등록하세요</p>
        </div>

        <div class="space-y-2.5 text-xs">
          <div>
            <label class="font-black text-slate-700 block mb-1">우리 아이 이름 (필수) 🐾</label>
            <input type="text" id="input-pet-name" placeholder="예: 뽀삐, 몽이, 두부, 초코" class="w-full p-3 rounded-2xl border border-slate-200 bg-slate-50 font-bold outline-none">
          </div>
          <div>
            <label class="font-black text-slate-700 block mb-1">견종 / 묘종 🐶</label>
            <input type="text" id="input-pet-breed" placeholder="예: 말티즈, 푸들, 포메라니안" class="w-full p-3 rounded-2xl border border-slate-200 bg-slate-50 font-medium outline-none">
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="font-black text-slate-700 block mb-1">나이 🎂</label>
              <input type="text" id="input-pet-age" placeholder="예: 3세" class="w-full p-3 rounded-2xl border border-slate-200 bg-slate-50 font-medium outline-none">
            </div>
            <div>
              <label class="font-black text-slate-700 block mb-1">체중 ⚖️</label>
              <input type="text" id="input-pet-weight" placeholder="예: 3.4kg" class="w-full p-3 rounded-2xl border border-slate-200 bg-slate-50 font-medium outline-none">
            </div>
          </div>
        </div>

        <button onclick="savePetProfile()" class="w-full py-3.5 rounded-2xl bg-orange-500 hover:bg-orange-600 text-white font-black text-xs shadow-lg transition-transform active:scale-98">
          내 아이 정보 등록하고 앱 맞춤 완성 ✨
        </button>
      </div>
    </div>

    <!-- Modal: Sitter Detail Profile -->
    <div id="modal-sitter-detail" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-md bg-white h-full sm:h-[90vh] sm:rounded-3xl flex flex-col border border-slate-200 animate-slide-up overflow-hidden text-left shadow-2xl">
        <div class="relative h-56 bg-slate-200 shrink-0">
          <img id="sitter-modal-img" src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&auto=format&fit=crop&q=80" class="w-full h-full object-cover">
          <button onclick="closeSitterDetailModal()" class="absolute top-3 right-3 p-2 rounded-full bg-black/50 text-white">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-5 space-y-4">
          <h3 id="sitter-modal-name" class="font-black text-lg text-slate-900">김은지 펫시터 ⭐ 4.98</h3>
          <p class="text-xs text-slate-500">서울 강남구 역삼동 • 도보 350m • 1박 71,600원</p>
          <div class="pt-2 flex gap-2">
            <button onclick="startSitterChat()" class="px-4 py-3 bg-slate-100 font-bold rounded-2xl text-xs">1:1 사전 채팅</button>
            <button onclick="requestSitterBooking()" class="flex-1 py-3 bg-orange-500 text-white font-black rounded-2xl text-xs shadow-md">돌봄 예약 신청</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Live Walking GPS Tracker -->
    <div id="modal-live-walk-gps" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-md bg-white h-full sm:h-[90vh] sm:rounded-3xl flex flex-col border border-slate-200 animate-slide-up overflow-hidden text-left shadow-2xl">
        <div class="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between shrink-0 bg-white">
          <div class="flex items-center gap-2">
            <div class="gps-pulse-marker"></div>
            <div>
              <h3 class="font-black text-sm text-slate-900">실시간 산책 LIVE GPS</h3>
              <p id="walk-live-title" class="text-[10px] text-slate-400">초코 & 김은지 펫시터</p>
            </div>
          </div>
          <button onclick="closeLiveWalkGpsModal()" class="p-1 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>
        <div class="relative h-64 bg-slate-100 shrink-0">
          <div id="live-walk-map-container" class="w-full h-full"></div>
        </div>
        <div class="flex-1 overflow-y-auto p-4 space-y-2">
          <div class="p-3 bg-amber-50 rounded-2xl border border-amber-200 flex items-center gap-2.5">
            <span class="text-2xl">💩</span>
            <div>
              <span class="text-xs font-black text-amber-900">14:20 황금변 완료 (인증샷 📸)</span>
              <p class="text-[10px] text-slate-500">역삼공원 산책로 • 정상 굳기</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: 10초 숏폼 멍스토리 -->
    <div id="modal-short-story" class="fixed inset-0 bg-black/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-sm h-full sm:h-[85vh] bg-slate-950 sm:rounded-3xl flex flex-col relative overflow-hidden text-white shadow-2xl">
        <div class="absolute top-6 left-4 right-4 z-30 flex items-center justify-between">
          <h4 id="story-pet-name" class="font-black text-xs text-white">초코의 오늘의 모먼트</h4>
          <button onclick="closeShortStoryModal()" class="p-1 rounded-full bg-black/40 text-white">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>
        <div class="flex-1 flex flex-col items-center justify-center relative p-6 text-center">
          <div class="text-7xl mb-4 animate-bounce" id="story-emoji-large">🧸</div>
          <h3 id="story-caption" class="text-lg font-black text-white">"장난감 터그놀이 삼매경 💕"</h3>
        </div>
        <div class="p-5 z-30 space-y-2 bg-gradient-to-t from-black via-black/80 to-transparent">
          <button onclick="shareStoryToInstagram()" class="w-full py-3 bg-gradient-to-r from-orange-500 to-pink-500 text-white font-black rounded-2xl text-xs shadow-lg">
            📷 인스타그램 스토리에 공유하기
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Social Auth (Kakao & Google) -->
    <div id="modal-auth" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-1.5">
            <span class="text-2xl">🐶🥕</span>
            <h3 class="font-black text-base text-slate-900">멍당근 간편 로그인</h3>
          </div>
          <button onclick="closeAuthModal()" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>
        <div class="text-center py-2">
          <div class="w-16 h-16 rounded-full bg-orange-50 mx-auto flex items-center justify-center text-3xl mb-2 shadow-inner">
            🥕
          </div>
          <h4 class="font-black text-sm text-slate-900">멍당근 시작하기</h4>
          <p class="text-xs text-slate-500 mt-1">소셜 계정으로 1초 가입하고<br>동네 이웃과 펫용품을 무료 나눔하세요!</p>
        </div>
        <div class="space-y-2">
          <button onclick="loginWithKakao()" class="w-full py-3 px-4 rounded-2xl bg-[#FEE500] hover:bg-[#FDD835] text-[#191919] font-black text-xs flex items-center justify-center gap-2.5 shadow-xs">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3C6.477 3 2 6.477 2 10.8c0 2.8 1.88 5.25 4.7 6.6l-.96 3.53c-.08.31.25.56.51.38l4.24-2.82c.49.07.99.11 1.51.11 5.523 0 10-3.477 10-7.8S17.523 3 12 3z"/>
            </svg>
            <span>카카오로 1초 시작하기</span>
          </button>
          <button onclick="loginWithGoogle()" class="w-full py-3 px-4 rounded-2xl bg-white hover:bg-slate-50 text-slate-800 font-bold text-xs flex items-center justify-center gap-2.5 border border-slate-300 shadow-xs">
            <svg class="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span>Google 계정으로 계속하기</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Free Trial Limit Reached -->
    <div id="modal-trial-limit" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl">
        <div class="flex justify-between items-center">
          <span class="text-sm font-black text-slate-900">🎁 1회 무료 체험 완료</span>
          <button onclick="closeTrialLimitModal()" class="p-1 rounded-full text-slate-400">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>
        <div class="text-center py-2">
          <div class="w-14 h-14 rounded-full bg-orange-50 mx-auto flex items-center justify-center text-3xl mb-2">🔒</div>
          <h4 class="font-black text-sm text-slate-900">비회원 1회 무료 체험 종료</h4>
          <p class="text-xs text-slate-500 mt-1">카카오/구글 1초 가입 시 모든 기능을 평생 무제한 무료로 이용하실 수 있습니다!</p>
        </div>
        <button onclick="closeTrialLimitModal(); loginWithKakao();" class="w-full py-3 rounded-2xl bg-[#FEE500] font-black text-xs">
          카카오로 1초 가입하고 무제한 무료 이용
        </button>
      </div>
    </div>

    <!-- Modal: Kakao Map Explorer -->
    <div id="modal-pet-map" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-md bg-white h-full sm:h-[90vh] sm:rounded-3xl flex flex-col border border-slate-200 animate-slide-up overflow-hidden text-left shadow-2xl">
        <div class="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between shrink-0 bg-white">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🗺️</span>
            <div>
              <h3 class="font-black text-sm text-slate-900">카카오 공식 펫 지도</h3>
              <p class="text-[10px] text-slate-400">현재 위치: 서울 강남구 역삼1동 (반경 1km)</p>
            </div>
          </div>
          <button onclick="closeMapModal()" class="p-1 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>
        <div class="relative h-64 bg-slate-100 shrink-0">
          <div id="kakao-map-container" class="w-full h-full"></div>
        </div>
        <div class="flex-1 overflow-y-auto p-4 space-y-2.5" id="map-places-container"></div>
      </div>
    </div>

    <!-- Modal: Sitter Register -->
    <div id="modal-sitter-register" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl">
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
          <span class="font-black text-base text-slate-900">🏠 펫시터 파트너 등록 신청</span>
          <button onclick="closeSitterRegisterModal()" class="p-1 text-slate-400"><i data-lucide="x" class="w-5 h-5"></i></button>
        </div>
        <div class="space-y-2 text-xs">
          <input type="text" id="reg-sitter-name" placeholder="펫시터 성함/닉네임" class="w-full p-2.5 rounded-xl border bg-slate-50">
          <input type="text" id="reg-sitter-addr" placeholder="활동 지역 (예: 역삼동)" class="w-full p-2.5 rounded-xl border bg-slate-50">
          <input type="number" id="reg-sitter-price" placeholder="1박 희망 요금 (원)" class="w-full p-2.5 rounded-xl border bg-slate-50 font-bold">
        </div>
        <button onclick="submitSitterRegister()" class="w-full py-3 bg-orange-500 text-white font-black rounded-2xl text-xs shadow-md">
          펫시터 파트너 신청하기
        </button>
      </div>
    </div>

    <!-- Modal: Compatibility & MBTI -->
    <div id="modal-compatibility" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl">
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
          <span class="text-xs font-black text-rose-600">💖 AI 멍냥 케미 분석</span>
          <button onclick="closeCompatibilityModal()" class="p-1 rounded-full text-slate-400"><i data-lucide="x" class="w-4 h-4"></i></button>
        </div>
        <div class="space-y-3 text-center">
          <div class="text-2xl font-black text-rose-600">케미 지수 95% 💕</div>
          <p class="text-xs font-bold text-slate-800">"환상의 산책 메이트! 서로의 에너지를 채워줘요."</p>
          <button onclick="alert('🎉 카톡 공유 링크가 복사되었습니다!');" class="w-full py-3 bg-[#FEE500] font-black rounded-2xl text-xs">
            카카오톡으로 공유하기 💬
          </button>
        </div>
      </div>
    </div>

  </div>

  <!-- Custom Scripts -->
  <script src="app.js"></script>
</body>
</html>"""

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(mungdanggeun_html)

print("index.html rebuilt with 멍당근 Centric Architecture and Mascot 🐶🥕")

# 3. Update app.js switchTab tabs list and titles
with open(app_file, 'r', encoding='utf-8') as f:
    js = f.read()

# Make sure tabs include sitter-explore
js = js.replace("tabs = ['home', 'ai', 'market', 'compat', 'chart', 'settings'];", "tabs = ['home', 'ai', 'sitter-explore', 'compat', 'chart', 'sitter-dashboard', 'settings'];")

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js updated.")
