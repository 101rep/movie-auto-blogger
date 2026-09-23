# -*- coding: utf-8 -*-
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
KAKAO_JS_KEY = "a0a8a6c45e622ea183ef6fc5ae3f3e5d"

# 1. New index.html with requested priority order:
# Priority 1: Free AI Photo Health Scanner
# Priority 2: AI Pet Compatibility & MBTI
# Priority 3: Nearby 24h Vets & 1km Radius Feed
# Priority 4: Doctor Chart & V-Check
# Priority 5: O2O Care & Settings

html_content = f"""<!DOCTYPE html>
<html lang="ko" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>펫로그 AI (PetLog AI) - 무료 AI 건강진단 & 멍냥궁합 & 스마트 차트</title>
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            brand: {{
              50: '#eef2ff',
              100: '#e0e7ff',
              500: '#4f46e5',
              600: '#4338ca',
              700: '#3730a3',
            }},
            meta: {{
              dark: '#000000',
              card: '#121212',
              border: '#262626',
              textMuted: '#a8a8a8'
            }}
          }}
        }}
      }}
    }}
  </script>

  <!-- Lucide Icons CDN -->
  <script src="https://unpkg.com/lucide@latest"></script>
  
  <!-- html2pdf.js for Doctor Chart Export -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>

  <!-- Kakao Map SDK -->
  <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}&libraries=services"></script>

  <!-- Custom Styles -->
  <link rel="stylesheet" href="style.css">
</head>
<body class="bg-gray-100 dark:bg-black text-gray-900 dark:text-gray-100 flex justify-center min-h-screen antialiased select-none">

  <!-- Mobile Frame Container -->
  <div id="app-container" class="w-full max-w-md bg-white dark:bg-black min-h-screen shadow-2xl relative flex flex-col pb-24 overflow-x-hidden border-x border-gray-200 dark:border-neutral-900">
    
    <!-- Top Status Bar Simulation -->
    <div class="sticky top-0 z-40 bg-white/90 dark:bg-black/90 backdrop-blur-md px-4 py-2 flex items-center justify-between border-b border-gray-100 dark:border-neutral-900 text-xs text-gray-500">
      <div class="font-semibold flex items-center gap-1.5 text-gray-800 dark:text-gray-200">
        <span id="current-time">09:19</span>
        <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
      </div>
      <div class="flex items-center gap-2">
        <i data-lucide="wifi" class="w-3.5 h-3.5"></i>
        <i data-lucide="signal" class="w-3.5 h-3.5"></i>
        <div class="flex items-center gap-0.5">
          <i data-lucide="battery" class="w-4 h-4 text-emerald-500"></i>
          <span class="text-[10px] font-bold">90%</span>
        </div>
      </div>
    </div>

    <!-- App Header -->
    <header class="px-4 py-3 flex items-center justify-between border-b border-gray-100 dark:border-neutral-900 bg-white dark:bg-black sticky top-8 z-30">
      <div class="flex items-center gap-2">
        <button id="btn-back-nav" onclick="switchTab('home')" class="hidden p-1 -ml-1 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-neutral-800 rounded-full">
          <i data-lucide="arrow-left" class="w-6 h-6"></i>
        </button>
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center text-white font-black text-sm shadow-md">
            🐾
          </div>
          <h1 id="header-title" class="text-lg font-bold tracking-tight">펫로그 AI</h1>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <!-- Theme Toggle -->
        <button onclick="toggleTheme()" class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800 text-gray-600 dark:text-gray-300" title="테마 변경">
          <i data-lucide="sun" class="w-5 h-5 dark:hidden"></i>
          <i data-lucide="moon" class="w-5 h-5 hidden dark:block"></i>
        </button>
        <!-- AI Instant Scanner Quick Button -->
        <button onclick="switchTab('ai')" class="flex items-center gap-1 px-2.5 py-1 bg-violet-50 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400 border border-violet-200 dark:border-violet-900/50 rounded-full text-xs font-semibold hover:scale-105 transition-transform">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
          <span>무료 AI검사</span>
        </button>
      </div>
    </header>

    <!-- Main Content Container -->
    <main id="tab-content" class="flex-1 overflow-y-auto">

      <!-- ================= 1. HOME TAB ================= -->
      <section id="view-home" class="tab-view space-y-4 p-4">
        
        <!-- Pet Profile Card -->
        <div class="bg-gradient-to-br from-indigo-600 to-violet-700 rounded-2xl p-4 text-white shadow-lg relative overflow-hidden">
          <div class="absolute -right-4 -bottom-4 opacity-20 text-8xl pointer-events-none">🐶</div>
          <div class="flex items-center gap-3">
            <div class="w-16 h-16 rounded-full border-2 border-white/50 overflow-hidden bg-white/20 flex items-center justify-center text-3xl shadow-inner">
              🐕
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h2 class="text-xl font-bold">초코 (Choco)</h2>
                <span class="text-xs px-2 py-0.5 rounded-full bg-white/20 font-medium">말티즈 • 3세</span>
              </div>
              <p class="text-xs text-indigo-100 mt-0.5">체중: 3.4kg | 정기검진 D-14</p>
              <div class="flex gap-2 mt-2">
                <span class="text-[11px] bg-emerald-400/20 text-emerald-200 border border-emerald-400/30 px-2 py-0.5 rounded-full font-medium flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> 오늘 건강 양호
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- [PRIORITY 1] FREE AI HEALTH SCANNER (무료 AI 사진 검사) -->
        <div class="bg-gradient-to-br from-violet-600 via-indigo-600 to-purple-700 text-white rounded-2xl p-4 shadow-lg space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1.5">
              <span class="text-xs bg-white/20 px-2 py-0.5 rounded-full font-bold flex items-center gap-1">
                <span>✨ 100% 무료</span>
                <span>• 무제한 검사</span>
              </span>
            </div>
            <span class="text-xs text-violet-200">Gemini Vision 탑재</span>
          </div>

          <div>
            <h3 class="font-black text-lg">📸 AI 1초 사진 건강 스캐너</h3>
            <p class="text-xs text-violet-100 mt-0.5">사진 한 장으로 피부 발진, 대변 상태, 안구 질환을 즉시 판별합니다.</p>
          </div>

          <!-- Quick Dropzone in Home -->
          <div onclick="switchTab('ai')" class="bg-white/10 hover:bg-white/15 border border-white/20 rounded-xl p-3.5 flex items-center justify-between cursor-pointer transition-all">
            <div class="flex items-center gap-2.5">
              <div class="w-10 h-10 rounded-full bg-white text-violet-700 flex items-center justify-center text-xl shadow">
                📷
              </div>
              <div>
                <p class="text-xs font-bold">터치하여 바로 사진 찍기 / 업로드</p>
                <p class="text-[10px] text-violet-200">피부 붉은기, 귀 안쪽, 대변, 눈물 자국 등</p>
              </div>
            </div>
            <i data-lucide="chevron-right" class="w-5 h-5 text-white"></i>
          </div>
        </div>

        <!-- [PRIORITY 2] AI COMPATIBILITY & MBTI & CALMING SIGNALS (멍냥 궁합 & 소통) -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-sm text-gray-800 dark:text-gray-100 flex items-center gap-1.5">
              <span>💖</span>
              <span>멍냥 케미 & AI 궁합 / 언어 번역</span>
            </h3>
            <span class="text-xs text-pink-600 dark:text-pink-400 font-bold">인스타 화제 🔥</span>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <!-- Compatibility Test Card -->
            <div onclick="openCompatibilityModal()" class="bg-gradient-to-br from-rose-500 to-pink-600 text-white rounded-2xl p-3.5 cursor-pointer shadow-md hover:opacity-95 transition-all space-y-1 relative overflow-hidden">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold bg-white/20 px-2 py-0.5 rounded-full">케미 분석</span>
                <span class="text-lg">🐶🐱</span>
              </div>
              <h4 class="font-black text-sm pt-1">멍냥 궁합 테스트</h4>
              <p class="text-[10px] text-rose-100">친구네 아이와 우리 아이 궁합 몇 점?</p>
            </div>

            <!-- MBTI Viral Card -->
            <div onclick="openViralModal()" class="bg-gradient-to-br from-purple-500 to-indigo-600 text-white rounded-2xl p-3.5 cursor-pointer shadow-md hover:opacity-95 transition-all space-y-1 relative overflow-hidden">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold bg-white/20 px-2 py-0.5 rounded-full">SNS 공유</span>
                <span class="text-lg">👑</span>
              </div>
              <h4 class="font-black text-sm pt-1">AI 관상 & MBTI</h4>
              <p class="text-[10px] text-purple-100">인스타 스토리 카드 1초 생성</p>
            </div>
          </div>

          <!-- Dog Language / Calming Signals Banner -->
          <div onclick="openDogTalkModal()" class="bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-2xl p-3.5 cursor-pointer shadow-md hover:opacity-95 transition-all flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center text-xl">
                💬
              </div>
              <div>
                <h4 class="font-bold text-xs">강아지 언어(카밍 시그널) AI 번역 백과</h4>
                <p class="text-[10px] text-emerald-100">하품, 기지개, 꼬리 흔들기... 무슨 뜻일까?</p>
              </div>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-emerald-200"></i>
          </div>
        </div>

        <!-- [PRIORITY 3] NEARBY 1KM RADIUS LIVE PLACES & KAKAO MAP -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-3">
          
          <div class="flex items-center justify-between border-b border-gray-100 dark:border-neutral-800 pb-2.5">
            <div>
              <div class="flex items-center gap-1.5 font-bold text-sm text-gray-800 dark:text-gray-100">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>내 주변 실시간 펫플레이스</span>
              </div>
              <p class="text-[10px] text-gray-400 mt-0.5">📍 <b class="text-indigo-600 dark:text-indigo-400">서울 강남구 역삼1동</b> (카카오맵 연동)</p>
            </div>
            
            <button onclick="refreshRadiusFeed()" class="flex items-center gap-1 px-2.5 py-1.5 bg-gray-100 dark:bg-neutral-800 hover:bg-gray-200 dark:hover:bg-neutral-700 text-gray-700 dark:text-gray-200 rounded-xl text-[11px] font-bold transition-all shadow-sm">
              <i data-lucide="rotate-cw" id="icon-refresh" class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400"></i>
              <span>새로고침</span>
            </button>
          </div>

          <!-- Radius Switcher -->
          <div class="flex items-center justify-between gap-2">
            <span class="text-[11px] font-bold text-gray-500 shrink-0">탐색 반경:</span>
            <div class="flex bg-gray-100 dark:bg-neutral-800 p-1 rounded-xl flex-1 justify-around text-xs">
              <button onclick="changeRadius(1)" id="radius-btn-1" class="radius-btn active flex-1 py-1 rounded-lg font-bold bg-white dark:bg-neutral-700 text-indigo-600 dark:text-indigo-400 shadow-sm transition-all text-center">반경 1km (도보)</button>
              <button onclick="changeRadius(3)" id="radius-btn-3" class="radius-btn flex-1 py-1 rounded-lg font-bold text-gray-500 dark:text-gray-400 transition-all text-center">3km</button>
              <button onclick="changeRadius(5)" id="radius-btn-5" class="radius-btn flex-1 py-1 rounded-lg font-bold text-gray-500 dark:text-gray-400 transition-all text-center">5km</button>
            </div>
          </div>

          <!-- Category Filter -->
          <div class="flex gap-1.5 overflow-x-auto pb-1 scrollbar-none text-[11px]">
            <button onclick="filterRadiusCategory('all')" class="feed-cat active px-2.5 py-1 rounded-lg font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-900/50 shrink-0">전체보기</button>
            <button onclick="filterRadiusCategory('vet')" class="feed-cat px-2.5 py-1 rounded-lg font-bold bg-gray-50 dark:bg-neutral-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-neutral-700 shrink-0">🏥 24시 동물병원</button>
            <button onclick="filterRadiusCategory('cafe')" class="feed-cat px-2.5 py-1 rounded-lg font-bold bg-gray-50 dark:bg-neutral-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-neutral-700 shrink-0">☕ 펫카페/식당</button>
            <button onclick="filterRadiusCategory('school')" class="feed-cat px-2.5 py-1 rounded-lg font-bold bg-gray-50 dark:bg-neutral-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-neutral-700 shrink-0">🎓 유치원/학교</button>
          </div>

          <!-- Live Feed Dynamic List -->
          <div id="radius-places-feed" class="space-y-2.5 pt-1 text-xs">
            <!-- Rendered by JS -->
          </div>

          <button onclick="openMapModal()" class="w-full py-2.5 bg-indigo-50 dark:bg-indigo-950/50 hover:bg-indigo-100 text-indigo-600 dark:text-indigo-400 font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 border border-indigo-200 dark:border-indigo-900/50">
            <i data-lucide="map" class="w-3.5 h-3.5"></i>
            <span>전체 카카오 지도 크게 보기</span>
          </button>
        </div>

        <!-- [PRIORITY 4] SMART DOCTOR CHART BANNER -->
        <div onclick="switchTab('chart')" class="bg-gradient-to-r from-red-500 to-rose-600 text-white rounded-2xl p-4 cursor-pointer shadow-md hover:opacity-95 transition-all flex items-center justify-between">
          <div class="space-y-1">
            <div class="flex items-center gap-1.5 text-xs font-bold bg-white/20 w-fit px-2 py-0.5 rounded-full">
              <i data-lucide="clipboard-pen" class="w-3.5 h-3.5"></i>
              <span>병원 원장님 전송 차트</span>
            </div>
            <h3 class="font-bold text-base">오늘 3초 V체크 기록하기</h3>
            <p class="text-xs text-rose-100">식욕, 배변, 구토, 약 복용 기록 $\rightarrow$ 원장님 1초 전송</p>
          </div>
          <i data-lucide="chevron-right" class="w-6 h-6 shrink-0"></i>
        </div>

        <!-- [PRIORITY 5] MONETIZATION & COMMERCE ADS -->
        <div class="space-y-2">
          <!-- 24h Hospital Sponsored -->
          <div class="bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-2xl p-3.5 shadow relative overflow-hidden border border-blue-700/50 flex items-center justify-between">
            <div>
              <span class="text-[9px] bg-blue-500/40 text-blue-200 px-2 py-0.5 rounded-full font-bold">AD • 공식 제휴</span>
              <h4 class="font-bold text-xs mt-1">📍 서울24시 동물의료센터 (연중무휴)</h4>
              <p class="text-[10px] text-blue-200">슬개골 탈구 • 치과 스케일링 • 심야 응급진료</p>
            </div>
            <div class="flex gap-1 shrink-0">
              <a href="tel:02-555-7582" class="px-2.5 py-1.5 bg-blue-600 text-white font-bold rounded-lg text-[10px]">전화</a>
              <button onclick="openKakaoRoute('서울24시 동물의료센터', '')" class="px-2.5 py-1.5 bg-white text-blue-900 font-bold rounded-lg text-[10px]">길찾기</button>
            </div>
          </div>

          <!-- Pet Insurance Banner -->
          <div onclick="clickAd('insurance', '3세 말티즈 맞춤 펫보험')" class="bg-gradient-to-r from-emerald-600 to-teal-700 text-white rounded-2xl p-3 shadow cursor-pointer hover:opacity-95 transition-all flex items-center justify-between">
            <div>
              <span class="text-[9px] bg-white/20 px-2 py-0.5 rounded-full font-bold">💰 병원비 최대 90% 보장</span>
              <h4 class="font-bold text-xs mt-0.5">초코(3세) 맞춤 펫보험 다이렉트 비교</h4>
            </div>
            <span class="text-[10px] bg-white/20 px-2 py-1 rounded-lg font-bold">비교하기 ></span>
          </div>
        </div>

      </section>

      <!-- ================= 2. AI DIAGNOSIS TAB (무료 AI 진단 전용) ================= -->
      <section id="view-ai" class="tab-view hidden p-4 space-y-4">
        
        <div class="bg-gradient-to-br from-violet-600 to-indigo-800 rounded-2xl p-4 text-white shadow-lg space-y-2">
          <div class="flex items-center gap-2">
            <div class="p-2 bg-white/20 rounded-xl text-xl">✨</div>
            <div>
              <h2 class="text-base font-bold">무료 AI 비전 건강 스캐너</h2>
              <p class="text-xs text-violet-100">사진 1장으로 피부·안구·대변 질환 사전 판별</p>
            </div>
          </div>
        </div>

        <!-- AI Image Upload & Scan -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-3">
          <h3 class="text-xs font-bold text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
            <i data-lucide="camera" class="w-4 h-4 text-indigo-500"></i>
            <span>진단할 부위 사진을 업로드하세요</span>
          </h3>

          <div id="ai-dropzone" onclick="triggerAIScan()" class="border-2 border-dashed border-gray-300 dark:border-neutral-700 rounded-2xl p-6 text-center cursor-pointer hover:border-indigo-500 transition-colors bg-gray-50 dark:bg-neutral-800/40">
            <div class="w-12 h-12 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 mx-auto flex items-center justify-center text-2xl mb-2">
              📸
            </div>
            <p class="text-xs font-bold text-gray-800 dark:text-gray-200">사진 촬영 또는 갤러리 선택 (터치)</p>
            <p class="text-[11px] text-gray-400 mt-1">대변, 피부 붉은 반점, 눈물 자국, 귀 안쪽 등</p>
          </div>

          <!-- AI Result Box -->
          <div id="ai-result-box" class="hidden space-y-3 pt-2">
            <div class="p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/50 rounded-xl space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-amber-700 dark:text-amber-300 flex items-center gap-1">
                  <i data-lucide="alert-triangle" class="w-3.5 h-3.5"></i>
                  <span>AI 분석 결과: 경미한 지루성 피부염 의심 (88%)</span>
                </span>
                <span class="text-[10px] bg-amber-200 dark:bg-amber-900 text-amber-800 dark:text-amber-200 px-1.5 py-0.5 rounded font-bold">주의</span>
              </div>
              <p class="text-[11px] text-amber-900 dark:text-amber-200 leading-relaxed">
                붉은 반점과 각질 패턴이 관찰됩니다. 습식 목욕 후 건조를 철저히 해주시고, 긁는 행동이 2일 이상 지속되면 동물병원에서 검사를 권장합니다.
              </p>
            </div>
            <button onclick="addAIResultToChart()" class="w-full py-2.5 bg-indigo-600 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 shadow">
              <i data-lucide="save" class="w-3.5 h-3.5"></i>
              <span>이 분석 결과를 닥터 차트에 자동 기록</span>
            </button>
          </div>
        </div>

        <!-- AI Voice Translator -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-bold flex items-center gap-1.5">
              <i data-lucide="mic" class="w-4 h-4 text-violet-500"></i>
              <span>AI 울음소리 / 행동 감정 분석기</span>
            </h3>
            <span class="text-[10px] bg-violet-100 dark:bg-violet-950 text-violet-600 dark:text-violet-300 px-2 py-0.5 rounded-full font-semibold">Beta</span>
          </div>
          <p class="text-xs text-gray-500 leading-relaxed">반려동물이 짖거나 낑낑거릴 때 5초간 녹음하면 감정 상태를 분석합니다.</p>
          <button onclick="simulateVoiceAnalysis()" id="btn-voice-record" class="w-full py-2.5 bg-violet-50 dark:bg-violet-950/50 border border-violet-200 dark:border-violet-900 text-violet-700 dark:text-violet-300 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5">
            <i data-lucide="play" class="w-3.5 h-3.5"></i>
            <span>울음소리 듣기 시작</span>
          </button>
          <p id="voice-analysis-result" class="hidden text-xs text-center font-bold text-violet-600 dark:text-violet-400 pt-1"></p>
        </div>

      </section>

      <!-- ================= 3. COMPATIBILITY & SOCIAL TAB (궁합 & 소통) ================= -->
      <section id="view-compat" class="tab-view hidden p-4 space-y-4">
        
        <div class="bg-gradient-to-br from-rose-500 to-pink-600 rounded-2xl p-4 text-white shadow-lg space-y-2">
          <div class="flex items-center gap-2">
            <span class="text-2xl">💖</span>
            <div>
              <h2 class="text-base font-bold">멍냥 케미 & AI 궁합 분석실</h2>
              <p class="text-xs text-rose-100">친구네 아이와 성향 궁합 & 산책 꿀팁 확인</p>
            </div>
          </div>
        </div>

        <!-- Interactive Matcher -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-3">
          <div class="flex items-center justify-center gap-3 py-2">
            <div class="text-center">
              <div class="w-14 h-14 rounded-full bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center text-3xl border-2 border-indigo-500">
                🐕
              </div>
              <span class="text-xs font-bold mt-1 block">우리 초코</span>
            </div>
            <div class="text-2xl font-black text-rose-500 animate-bounce">❤️</div>
            <div class="text-center">
              <select id="compat-partner-select-tab" onchange="calcCompatibilityTab()" class="w-24 text-xs p-1.5 rounded-lg bg-gray-100 dark:bg-neutral-800 border border-gray-300 dark:border-neutral-700 font-bold">
                <option value="poodle">토이푸들 뽀삐</option>
                <option value="retriever">리트리버 몽이</option>
                <option value="cat_luna">고양이 루나</option>
                <option value="corgi">웰시코기 둥이</option>
              </select>
              <span class="text-xs font-bold mt-1 block">친구 아이</span>
            </div>
          </div>

          <!-- Compatibility Result Box -->
          <div class="bg-gradient-to-br from-rose-500 to-purple-600 rounded-2xl p-4 text-white space-y-2 shadow-lg">
            <div class="flex justify-between items-center">
              <span class="text-xs font-bold bg-white/20 px-2 py-0.5 rounded-full">케미 지수</span>
              <span class="text-2xl font-black" id="compat-score-tab">96점</span>
            </div>
            <h4 class="font-bold text-sm" id="compat-title-tab">"찰떡궁합! 평생 단짝 베프"</h4>
            <p class="text-xs text-rose-100 leading-relaxed" id="compat-desc-tab">
              초코의 활발한 성격과 뽀삐의 다정한 성향이 완벽히 조화를 이룹니다. 함께 산책하면 에너지를 기분 좋게 발산할 수 있습니다.
            </p>
            <div class="text-[10px] text-rose-200 bg-black/20 p-2 rounded-lg mt-2">
              💡 <b>합사/산책 꿀팁</b>: 첫 만남 때는 좁은 공간보다 넓은 공원에서 나란히 걷는 평행 산책부터 시작하세요!
            </div>
          </div>

          <button onclick="shareCompatibility()" class="w-full py-3 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow">
            <span>친구에게 궁합 결과 공유하기 (인스타/카톡)</span>
          </button>
        </div>

        <!-- Dongne Friends List -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-xs flex items-center gap-1.5">
              <span>🐕</span>
              <span>우리 동네 산책 짝꿍 매칭</span>
            </h3>
            <span class="text-[10px] text-indigo-500 font-bold">실시간 2명 대기중</span>
          </div>

          <div class="space-y-2 text-xs">
            <div class="p-2.5 bg-gray-50 dark:bg-neutral-800/60 rounded-xl flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-2xl">🐩</span>
                <div>
                  <p class="font-bold">뽀삐 (토이푸들, 2세)</p>
                  <p class="text-[10px] text-gray-400">초코와 궁합 96% • 역삼공원 산책</p>
                </div>
              </div>
              <button onclick="requestWalkMate('뽀삐')" class="px-2.5 py-1.5 bg-indigo-600 text-white rounded-lg text-[10px] font-bold">산책 신청</button>
            </div>

            <div class="p-2.5 bg-gray-50 dark:bg-neutral-800/60 rounded-xl flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-2xl">🦮</span>
                <div>
                  <p class="font-bold">몽이 (리트리버, 4세)</p>
                  <p class="text-[10px] text-gray-400">초코와 궁합 88% • 순한 성격</p>
                </div>
              </div>
              <button onclick="requestWalkMate('몽이')" class="px-2.5 py-1.5 bg-indigo-600 text-white rounded-lg text-[10px] font-bold">산책 신청</button>
            </div>
          </div>
        </div>

      </section>

      <!-- ================= 4. DOCTOR CHART TAB (병원 전송 차트) ================= -->
      <section id="view-chart" class="tab-view hidden p-4 space-y-4">
        
        <div class="bg-gradient-to-r from-red-500 to-rose-600 rounded-2xl p-4 text-white shadow-lg space-y-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="p-2 bg-white/20 rounded-xl">
                <i data-lucide="file-heart" class="w-6 h-6"></i>
              </div>
              <div>
                <h2 class="text-lg font-bold">스마트 닥터 차트</h2>
                <p class="text-xs text-rose-100">동물병원 원장님 전송용 홈케어 일지</p>
              </div>
            </div>
          </div>
          <div class="pt-2 flex gap-2">
            <button onclick="openSendModal()" class="flex-1 bg-white text-red-600 font-bold py-2.5 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-md">
              <i data-lucide="send" class="w-4 h-4"></i>
              <span>원장님께 차트 전송 (PDF/링크)</span>
            </button>
            <button onclick="generateChartPDF()" class="bg-black/30 hover:bg-black/40 text-white font-semibold py-2.5 px-3 rounded-xl text-xs flex items-center justify-center gap-1">
              <i data-lucide="download" class="w-4 h-4"></i>
              <span>PDF</span>
            </button>
          </div>
        </div>

        <!-- V-Check Form -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-4">
          <div class="flex items-center justify-between border-b border-gray-100 dark:border-neutral-800 pb-2">
            <div class="font-bold text-sm flex items-center gap-1.5">
              <i data-lucide="check-square" class="w-4 h-4 text-emerald-500"></i>
              <span>오늘의 원터치 V-체크</span>
            </div>
            <input type="date" id="chart-date-input" class="text-xs bg-gray-100 dark:bg-neutral-800 border-none rounded-lg px-2 py-1 font-medium">
          </div>

          <!-- 1. Appetite -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-gray-600 dark:text-gray-400">🍚 식사/식욕 상태</label>
            <div class="grid grid-cols-4 gap-1.5" id="group-appetite">
              <button type="button" onclick="selectCheck(this, 'appetite', '정상')" class="check-btn active py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800">정상</button>
              <button type="button" onclick="selectCheck(this, 'appetite', '약간감소')" class="check-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800">약간감소</button>
              <button type="button" onclick="selectCheck(this, 'appetite', '거부(안먹음)')" class="check-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800 text-red-500">거부</button>
              <button type="button" onclick="selectCheck(this, 'appetite', '과식')" class="check-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800">과식</button>
            </div>
          </div>

          <!-- 2. Stool -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-gray-600 dark:text-gray-400">💩 배변/배뇨 상태</label>
            <div class="grid grid-cols-4 gap-1.5" id="group-stool">
              <button type="button" onclick="selectCheck(this, 'stool', '정상변')" class="check-btn active py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800">정상변</button>
              <button type="button" onclick="selectCheck(this, 'stool', '묽은변/설사')" class="check-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800 text-amber-500">설사</button>
              <button type="button" onclick="selectCheck(this, 'stool', '혈변')" class="check-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800 text-red-500">혈변</button>
              <button type="button" onclick="selectCheck(this, 'stool', '변비')" class="check-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800">변비</button>
            </div>
          </div>

          <!-- 3. Symptoms -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-gray-600 dark:text-gray-400">⚠️ 이상 증상 (중복 선택 가능)</label>
            <div class="grid grid-cols-3 gap-1.5" id="group-symptoms">
              <button type="button" onclick="toggleMultiCheck(this, '구토')" class="symptom-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800">🤮 구토</button>
              <button type="button" onclick="toggleMultiCheck(this, '기침/호흡')" class="symptom-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800">😮‍💨 기침/호흡</button>
              <button type="button" onclick="toggleMultiCheck(this, '가려움/긁음')" class="symptom-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800">🐾 가려움/긁음</button>
              <button type="button" onclick="toggleMultiCheck(this, '다리절음')" class="symptom-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800">🦵 다리절음</button>
              <button type="button" onclick="toggleMultiCheck(this, '기력저하')" class="symptom-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800">😴 기력저하</button>
              <button type="button" onclick="toggleMultiCheck(this, '눈물/눈곱')" class="symptom-btn py-2 text-xs rounded-xl border bg-gray-50 dark:bg-neutral-800">👀 눈물/눈곱</button>
            </div>
          </div>

          <!-- 4. Medication -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-gray-600 dark:text-gray-400">💊 투약 기록</label>
            <div class="flex gap-2">
              <label class="flex items-center gap-1.5 text-xs bg-gray-50 dark:bg-neutral-800 px-3 py-2 rounded-xl border flex-1 cursor-pointer">
                <input type="checkbox" id="med-morning" class="rounded text-indigo-600">
                <span>아침 약 복용</span>
              </label>
              <label class="flex items-center gap-1.5 text-xs bg-gray-50 dark:bg-neutral-800 px-3 py-2 rounded-xl border flex-1 cursor-pointer">
                <input type="checkbox" id="med-evening" class="rounded text-indigo-600">
                <span>저녁 약 복용</span>
              </label>
            </div>
          </div>

          <!-- 5. Memo -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-gray-600 dark:text-gray-400">📝 원장님께 전할 메모</label>
            <textarea id="chart-memo-input" rows="2" placeholder="예: 아침 노란 거품토 1회 발생. 산책 후 발을 계속 핥음" class="w-full text-xs p-3 rounded-xl bg-gray-50 dark:bg-neutral-800 border focus:outline-none"></textarea>
          </div>

          <button onclick="saveHealthLog()" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow">
            <i data-lucide="plus-circle" class="w-4 h-4"></i>
            <span>차트에 오늘 기록 저장하기</span>
          </button>
        </div>

        <!-- History Timeline -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-sm">누적 헬스케어 타임라인</h3>
            <span class="text-xs text-gray-400" id="chart-log-count">총 3건</span>
          </div>
          <div id="doctor-chart-history" class="space-y-2.5">
            <!-- Rendered by JS -->
          </div>
        </div>

      </section>

      <!-- ================= 5. SETTINGS & META UI TAB (설정) ================= -->
      <section id="view-settings" class="tab-view hidden p-2 space-y-1">
        
        <div class="bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-4 mb-3 space-y-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-neutral-200 dark:bg-neutral-800 flex items-center justify-center text-lg">
                👤
              </div>
              <div>
                <div class="flex items-center gap-1.5">
                  <span class="font-bold text-sm">계정 센터</span>
                  <span class="text-[10px] text-gray-400 font-semibold">∞ Meta</span>
                </div>
                <p class="text-[11px] text-gray-500">보안, 개인정보, 알림 기본 설정</p>
              </div>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </div>
        </div>

        <div class="space-y-0.5 text-sm">
          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="user-plus" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>친구 초대 & 궁합 공유</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="bell" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>백신 / 심장사상충 알림 설정</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="lock" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>개인정보 보호 & GPS 위치 권한</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="info" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>앱 버전 및 정보 (v2.5.0 최신판)</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>
        </div>

      </section>

    </main>

    <!-- Bottom Navigation Bar (5 Primary Tabs) -->
    <nav class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white/95 dark:bg-black/95 backdrop-blur-lg border-t border-gray-200 dark:border-neutral-900 px-2 py-2 flex justify-around z-40">
      
      <button onclick="switchTab('home')" id="nav-home" class="nav-btn active flex flex-col items-center gap-1 text-indigo-600 dark:text-indigo-400 flex-1 py-1">
        <i data-lucide="home" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">홈</span>
      </button>

      <button onclick="switchTab('ai')" id="nav-ai" class="nav-btn flex flex-col items-center gap-1 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex-1 py-1">
        <i data-lucide="sparkles" class="w-5 h-5 text-violet-500"></i>
        <span class="text-[10px] font-bold">무료AI진단</span>
      </button>

      <button onclick="switchTab('compat')" id="nav-compat" class="nav-btn flex flex-col items-center gap-1 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex-1 py-1">
        <i data-lucide="heart" class="w-5 h-5 text-rose-500"></i>
        <span class="text-[10px] font-bold">멍냥궁합</span>
      </button>

      <button onclick="switchTab('chart')" id="nav-chart" class="nav-btn flex flex-col items-center gap-1 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex-1 py-1">
        <div class="relative">
          <i data-lucide="clipboard-pen" class="w-5 h-5"></i>
          <span class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-red-500"></span>
        </div>
        <span class="text-[10px] font-bold">닥터차트</span>
      </button>

      <button onclick="switchTab('settings')" id="nav-settings" class="nav-btn flex flex-col items-center gap-1 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex-1 py-1">
        <i data-lucide="settings" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">설정</span>
      </button>

    </nav>

    <!-- ================= MODALS ================= -->

    <!-- Modal: Kakao Map Explorer -->
    <div id="modal-pet-map" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-md bg-white dark:bg-neutral-900 h-full sm:h-[90vh] sm:rounded-3xl flex flex-col border border-gray-200 dark:border-neutral-800 animate-slide-up overflow-hidden text-left">
        <div class="px-4 py-3 border-b border-gray-100 dark:border-neutral-800 flex items-center justify-between shrink-0">
          <div class="flex items-center gap-2">
            <span class="text-xl">🗺️</span>
            <div>
              <h3 class="font-bold text-sm">카카오 공식 펫 지도</h3>
              <p class="text-[10px] text-gray-400">현재 위치: 서울 강남구 역삼1동</p>
            </div>
          </div>
          <button onclick="closeMapModal()" class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>

        <!-- Kakao Map Canvas -->
        <div class="relative h-60 bg-slate-100 dark:bg-neutral-800 overflow-hidden shrink-0 border-b border-gray-200 dark:border-neutral-800">
          <div id="kakao-map-container" class="w-full h-full"></div>
          <button onclick="getUserGPSLocation()" class="absolute bottom-3 right-3 bg-white dark:bg-neutral-800 text-gray-800 dark:text-gray-200 p-2.5 rounded-full shadow-xl border z-10" title="내 위치">
            <i data-lucide="crosshair" class="w-4 h-4 text-indigo-600 dark:text-indigo-400"></i>
          </button>
        </div>

        <!-- Place List -->
        <div class="flex-1 overflow-y-auto p-4 space-y-2.5" id="map-places-container"></div>
      </div>
    </div>

    <!-- Modal: Compatibility & MBTI -->
    <div id="modal-compatibility" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white dark:bg-neutral-900 rounded-3xl p-5 space-y-4 border border-gray-200 dark:border-neutral-800 animate-slide-up text-left">
        <div class="flex justify-between items-center border-b border-gray-100 dark:border-neutral-800 pb-2">
          <span class="text-xs font-bold text-rose-600 dark:text-rose-400">💖 AI 멍냥 궁합 분석</span>
          <button onclick="closeCompatibilityModal()" class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <div class="space-y-3">
          <div class="flex items-center justify-center gap-3 py-2">
            <div class="text-center">
              <div class="w-14 h-14 rounded-full bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center text-3xl border-2 border-indigo-500">🐕</div>
              <span class="text-xs font-bold mt-1 block">우리 초코</span>
            </div>
            <div class="text-2xl font-black text-rose-500 animate-bounce">❤️</div>
            <div class="text-center">
              <select id="compat-partner-select" onchange="calcCompatibility()" class="w-24 text-xs p-1.5 rounded-lg bg-gray-100 dark:bg-neutral-800 border font-bold">
                <option value="poodle">토이푸들 뽀삐</option>
                <option value="retriever">리트리버 몽이</option>
                <option value="cat_luna">고양이 루나</option>
                <option value="corgi">웰시코기 둥이</option>
              </select>
              <span class="text-xs font-bold mt-1 block">친구 아이</span>
            </div>
          </div>

          <div class="bg-gradient-to-br from-rose-500 to-purple-600 rounded-2xl p-4 text-white space-y-2 shadow-lg">
            <div class="flex justify-between items-center">
              <span class="text-xs font-bold bg-white/20 px-2 py-0.5 rounded-full">케미 지수</span>
              <span class="text-2xl font-black" id="compat-score">96점</span>
            </div>
            <h4 class="font-bold text-sm" id="compat-title">"찰떡궁합! 평생 단짝 베프"</h4>
            <p class="text-xs text-rose-100 leading-relaxed" id="compat-desc">
              초코의 활발한 성격과 뽀삐의 다정한 성향이 완벽히 조화를 이룹니다.
            </p>
          </div>

          <button onclick="shareCompatibility()" class="w-full py-3 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl text-xs">
            친구에게 결과 공유하기 (인스타/카톡)
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Viral MBTI -->
    <div id="modal-viral-mbti" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white dark:bg-neutral-900 rounded-3xl p-5 space-y-4 border animate-slide-up text-left">
        <div class="flex justify-between items-center border-b pb-2">
          <span class="text-xs font-bold text-purple-600">👑 AI 멍냥 관상 & MBTI</span>
          <button onclick="closeViralModal()"><i data-lucide="x" class="w-4 h-4"></i></button>
        </div>
        <div class="bg-gradient-to-tr from-pink-500 via-purple-600 to-indigo-600 rounded-2xl p-5 text-white space-y-3">
          <div class="flex justify-between">
            <span class="text-2xl">👑</span>
            <span class="text-[10px] bg-white/20 px-2 py-0.5 rounded-full font-bold">MBTI: ENFP (재롱둥이형)</span>
          </div>
          <h3 class="text-xl font-black">초코의 관상 분석</h3>
          <p class="text-xs text-pink-100">"평생 사랑받을 사랑둥이 눈망울과 간식 레이더형 코"</p>
          <div class="bg-black/30 p-2.5 rounded-xl text-xs space-y-0.5">
            <p>💖 친화력: 99점</p>
            <p>🍖 식탐력: 95점</p>
            <p>👑 자기애: 92점</p>
          </div>
        </div>
        <button onclick="shareToInstagram()" class="w-full py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold rounded-xl text-xs">
          인스타 스토리 / 카톡 공유하기
        </button>
      </div>
    </div>

    <!-- Modal: Dog Talk (Calming Signals) -->
    <div id="modal-dogtalk" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white dark:bg-neutral-900 rounded-3xl p-5 space-y-4 border animate-slide-up max-h-[85vh] overflow-y-auto text-left">
        <div class="flex justify-between items-center border-b pb-2">
          <span class="text-xs font-bold text-emerald-600">💬 강아지 언어(카밍 시그널) 백과</span>
          <button onclick="closeDogTalkModal()"><i data-lucide="x" class="w-4 h-4"></i></button>
        </div>
        <div class="space-y-2 text-xs">
          <div class="p-3 bg-emerald-50 dark:bg-emerald-950/40 rounded-xl space-y-1">
            <b class="text-emerald-800 dark:text-emerald-200">🙇 플레이 바우 (상체 낮추고 엉덩이 들기)</b>
            <p class="text-emerald-950 dark:text-emerald-300">"나 너랑 친구하고 싶어! 신나게 뛰어놀래?"</p>
          </div>
          <div class="p-3 bg-amber-50 dark:bg-amber-950/40 rounded-xl space-y-1">
            <b class="text-amber-800 dark:text-amber-200">🥱 갑자기 하품하기 / 시선 피하기</b>
            <p class="text-amber-950 dark:text-amber-300">"나 긴장했어. 우리 흥분을 가라앉히자."</p>
          </div>
          <div class="p-3 bg-blue-50 dark:bg-blue-950/40 rounded-xl space-y-1">
            <b class="text-blue-800 dark:text-blue-200">👅 코와 입술을 날름 핥기</b>
            <p class="text-blue-950 dark:text-blue-300">"스트레스를 스스로 달래는 중이에요."</p>
          </div>
        </div>
        <button onclick="alert('📸 사진 업로드 시 AI가 행동을 자동 판별합니다!')" class="w-full py-3 bg-emerald-600 text-white font-bold rounded-xl text-xs">
          사진 찍어 행동 번역하기
        </button>
      </div>
    </div>

    <!-- Modal: Send Doctor Chart -->
    <div id="modal-send-chart" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-end sm:items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-md bg-white dark:bg-neutral-900 rounded-t-3xl sm:rounded-3xl p-5 space-y-4 max-h-[85vh] overflow-y-auto border text-left">
        <div class="flex items-center justify-between border-b pb-3">
          <h3 class="font-bold text-base">🩺 동물병원 원장님께 전송하기</h3>
          <button onclick="closeSendModal()"><i data-lucide="x" class="w-5 h-5"></i></button>
        </div>
        <div class="bg-indigo-50 dark:bg-indigo-950/50 p-3 rounded-2xl text-xs space-y-1">
          <p class="font-bold text-indigo-700">✨ AI 3줄 사전 문진 브리핑</p>
          <ul class="text-indigo-950 dark:text-indigo-200 list-disc list-inside space-y-0.5">
            <li>최근 3일간 식욕 정상 (오늘 약간 감소 1회)</li>
            <li>이상 증상: 노란 거품토 1회, 발바닥 가려움 2회</li>
            <li>투약: 정기 심장사상충 완료</li>
          </ul>
        </div>
        <select id="hospital-select" class="w-full text-xs p-3 rounded-xl bg-gray-50 dark:bg-neutral-800 border">
          <option value="seoul24">📍 서울24시 동물의료센터 (김진우 수의사)</option>
          <option value="gangnam">📍 강남 펫종합병원 (이서연 수의사)</option>
        </select>
        <button onclick="executeHospitalSend('direct')" class="w-full py-3 bg-red-600 text-white font-bold rounded-xl text-xs">
          지정 병원 EMR 전자차트로 즉시 전송
        </button>
      </div>
    </div>

    <!-- Printable PDF (Hidden) -->
    <div id="printable-pdf-chart" class="hidden p-8 bg-white text-black font-sans">
      <h1 class="text-xl font-bold mb-4">🐾 스마트 펫 헬스케어 임상 차트</h1>
      <table class="w-full text-xs border-collapse border border-gray-300">
        <thead>
          <tr class="bg-gray-100"><th class="p-2 border">일자</th><th class="p-2 border">식욕</th><th class="p-2 border">배변</th><th class="p-2 border">증상</th><th class="p-2 border">메모</th></tr>
        </thead>
        <tbody id="pdf-table-body"></tbody>
      </table>
    </div>

  </div>

  <!-- Custom Scripts -->
  <script src="app.js"></script>
</body>
</html>
"""

# 2. Rebuilt app.js with bulletproof function exports and error handling
js_content = f"""// PetLog AI Bulletproof Logic

// Global Health Logs State
let healthLogs = [
  {{ id: 1, date: '2026-09-18', appetite: '정상', stool: '정상변', symptoms: [], medMorning: true, medEvening: false, memo: '아침 사료 완식. 산책 38분 완료.' }},
  {{ id: 2, date: '2026-09-17', appetite: '약간감소', stool: '묽은변/설사', symptoms: ['구토', '가려움/긁음'], medMorning: true, medEvening: true, memo: '새벽 6시 노란 거품토 1회. 발바닥을 계속 핥음.' }},
  {{ id: 3, date: '2026-09-16', appetite: '정상', stool: '정상변', symptoms: ['눈물/눈곱'], medMorning: true, medEvening: true, memo: '눈물 자국 전용 세정제로 닦아줌.' }}
];

let currentSelectedAppetite = '정상';
let currentSelectedStool = '정상변';
let currentSelectedSymptoms = [];
let currentMapFilter = 'all';
let selectedRadius = 1;
let selectedRadiusCategory = 'all';

// Real Radius Places Dataset
const radiusDataset = [
  {{ id: 101, name: '서울24시 동물의료센터', category: 'vet', distKm: 0.35, distanceStr: '350m (도보 4분)', status: '🟢 실시간 진료중 (24시 야간)', summary: '슬개골 탈구 전문 • 심야 응급실 상시 운영 • 고양이 친화 인증', phone: '02-555-7582', icon: '🏥', rating: '⭐ 4.9' }},
  {{ id: 102, name: '어반포포 반려견 동반 브런치', category: 'cafe', distKm: 0.45, distanceStr: '450m (도보 6분)', status: '🟢 영업중 (~22:00)', summary: '실내/테라스 애견동반 • 무료 멍푸치노 제공 • 반려견 수제간식', phone: '02-345-1288', icon: '☕', rating: '⭐ 4.8' }},
  {{ id: 103, name: '도그스쿨 강남 애견 유치원 & 행동교정', category: 'school', distKm: 0.72, distanceStr: '720m (도보 9분)', status: '🟢 상담 가능 (~20:00)', summary: '전문 훈련사 상주 • 실시간 CCTV 알림장 • 1km 이내 등하원 픽업', phone: '02-777-3321', icon: '🎓', rating: '⭐ 5.0' }},
  {{ id: 104, name: '폼폼 펫 그루밍 & 24시 무인용품샵', category: 'grooming', distKm: 0.88, distanceStr: '880m (도보 11분)', status: '🟢 24시 무인영업', summary: '저자극 탄산 스파 미용 • 밤샘 급한 사료/패드 키오스크 구매 가능', phone: '02-888-1234', icon: '✂️', rating: '⭐ 4.7' }},
  {{ id: 105, name: '바른 펫 한방 재활 동물병원', category: 'vet', distKm: 2.1, distanceStr: '2.1km (차량 6분)', status: '🟢 진료중 (~19:00)', summary: '침치료 • 수중 재활 런닝머신 • 노령견 만성질환 케어 전문', phone: '02-666-4321', icon: '🏥', rating: '⭐ 4.9' }},
  {{ id: 106, name: '강남 반려견 힐링 테마파크 & 수영장', category: 'school', distKm: 4.2, distanceStr: '4.2km (차량 12분)', status: '🟢 영업중 (~21:00)', summary: '1,000평 천연잔디 운동장 • 온수 애견 수영장 • 셀프 목욕실 완비', phone: '02-999-5566', icon: '🏊', rating: '⭐ 4.9' }}
];

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', () => {{
  if (window.lucide) lucide.createIcons();
  
  const today = new Date().toISOString().split('T')[0];
  const dateInput = document.getElementById('chart-date-input');
  if (dateInput) dateInput.value = today;

  renderChartHistory();
  renderRadiusFeedList();
  updateLiveClock();
  setInterval(updateLiveClock, 30000);
}});

// 1. Tab Switcher
window.switchTab = function(tabId) {{
  const tabs = ['home', 'ai', 'compat', 'chart', 'settings'];
  const titles = {{
    home: '펫로그 AI',
    ai: '무료 AI 건강 스캐너',
    compat: '멍냥 케미 & 궁합 분석',
    chart: '스마트 닥터 차트',
    settings: '설정'
  }};

  tabs.forEach(t => {{
    const view = document.getElementById(`view-${{t}}`);
    const nav = document.getElementById(`nav-${{t}}`);
    if (t === tabId) {{
      if (view) view.classList.remove('hidden');
      if (nav) {{
        nav.classList.add('active');
        nav.classList.remove('text-gray-400');
      }}
    }} else {{
      if (view) view.classList.add('hidden');
      if (nav) {{
        nav.classList.remove('active');
        nav.classList.add('text-gray-400');
      }}
    }}
  }});

  const headerTitle = document.getElementById('header-title');
  const backNav = document.getElementById('btn-back-nav');
  if (headerTitle) headerTitle.textContent = titles[tabId] || '펫로그 AI';
  if (backNav) {{
    if (tabId !== 'home') backNav.classList.remove('hidden');
    else backNav.classList.add('hidden');
  }}

  if (window.lucide) lucide.createIcons();
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}};

// 2. Theme Toggle
window.toggleTheme = function() {{
  const html = document.documentElement;
  if (html.classList.contains('dark')) {{
    html.classList.remove('dark');
  }} else {{
    html.classList.add('dark');
  }}
}};

function updateLiveClock() {{
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const el = document.getElementById('current-time');
  if (el) el.textContent = `${{hours}}:${{minutes}}`;
}}

// 3. AI Scanner Functions
window.triggerAIScan = function() {{
  const dropzone = document.getElementById('ai-dropzone');
  const resultBox = document.getElementById('ai-result-box');
  if (!dropzone || !resultBox) return;

  dropzone.innerHTML = `
    <div class="py-4 space-y-2">
      <div class="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p class="text-xs font-bold text-indigo-600 dark:text-indigo-400">Gemini 비전 AI 분석 중...</p>
      <p class="text-[10px] text-gray-400">피부 병변 및 염증 지수를 계산하고 있습니다.</p>
    </div>
  `;

  setTimeout(() => {{
    dropzone.innerHTML = `
      <div class="text-center py-2">
        <span class="text-2xl">🔍</span>
        <p class="text-xs font-bold text-emerald-600">분석 완료 (재업로드 터치)</p>
      </div>
    `;
    resultBox.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  }}, 1000);
}};

window.addAIResultToChart = function() {{
  const newLog = {{
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    appetite: '정상',
    stool: '정상변',
    symptoms: ['가려움/긁음'],
    medMorning: true,
    medEvening: false,
    memo: '[AI 진단 자동 기록] 피부 발진 및 지루성 피부염 88% 의심 소견 기록됨.'
  }};

  healthLogs.unshift(newLog);
  renderChartHistory();
  alert('✅ AI 분석 결과가 닥터 차트에 성공적으로 반영되었습니다.');
  switchTab('chart');
}};

window.simulateVoiceAnalysis = function() {{
  const btn = document.getElementById('btn-voice-record');
  const result = document.getElementById('voice-analysis-result');
  if (!btn || !result) return;

  btn.innerHTML = '<span class="animate-pulse">🎙️ 5초간 소리를 듣고 있습니다...</span>';
  setTimeout(() => {{
    btn.innerHTML = '<span>다시 녹음하기</span>';
    result.classList.remove('hidden');
    result.textContent = '🔊 분석 결과: "놀아줘요! 심심해요" (요구성 짖음 92%)';
  }}, 1500);
}};

// 4. Compatibility & MBTI
window.openCompatibilityModal = function() {{
  const modal = document.getElementById('modal-compatibility');
  if (modal) modal.classList.remove('hidden');
  calcCompatibility();
  if (window.lucide) lucide.createIcons();
}};

window.closeCompatibilityModal = function() {{
  const modal = document.getElementById('modal-compatibility');
  if (modal) modal.classList.add('hidden');
}};

window.calcCompatibility = function() {{
  const select = document.getElementById('compat-partner-select');
  const partner = select ? select.value : 'poodle';
  const data = {{
    poodle: {{ score: '96점', title: '"찰떡궁합! 평생 단짝 베프"', desc: '초코의 활발한 성격과 뽀삐의 다정한 성향이 완벽히 조화를 이룹니다.' }},
    retriever: {{ score: '88점', title: '"든든한 맏형과 막내 케미"', desc: '대형견 몽이의 의젓함이 초코에게 큰 안정감을 줍니다.' }},
    cat_luna: {{ score: '72점', title: '"밀당하는 톰과 제리"', desc: '고양이 루나의 독립적인 성향에 맞춰 초코가 거리를 조절해야 합니다.' }},
    corgi: {{ score: '91점', title: '"에너지 폭발! 우다다 콤비"', desc: '활동량이 넘치는 두 아이가 만나면 신나게 뛰어놀 수 있습니다.' }}
  }};

  const item = data[partner] || data.poodle;
  const scoreEl = document.getElementById('compat-score');
  const titleEl = document.getElementById('compat-title');
  const descEl = document.getElementById('compat-desc');

  if (scoreEl) scoreEl.textContent = item.score;
  if (titleEl) titleEl.textContent = item.title;
  if (descEl) descEl.textContent = item.desc;
}};

window.calcCompatibilityTab = function() {{
  const select = document.getElementById('compat-partner-select-tab');
  const partner = select ? select.value : 'poodle';
  const data = {{
    poodle: {{ score: '96점', title: '"찰떡궁합! 평생 단짝 베프"', desc: '초코의 활발한 성격과 뽀삐의 다정한 성향이 완벽히 조화를 이룹니다.' }},
    retriever: {{ score: '88점', title: '"든든한 맏형과 막내 케미"', desc: '대형견 몽이의 의젓함이 초코에게 큰 안정감을 줍니다.' }},
    cat_luna: {{ score: '72점', title: '"밀당하는 톰과 제리"', desc: '고양이 루나의 독립적인 성향에 맞춰 초코가 거리를 조절해야 합니다.' }},
    corgi: {{ score: '91점', title: '"에너지 폭발! 우다다 콤비"', desc: '활동량이 넘치는 두 아이가 만나면 신나게 뛰어놀 수 있습니다.' }}
  }};

  const item = data[partner] || data.poodle;
  const scoreEl = document.getElementById('compat-score-tab');
  const titleEl = document.getElementById('compat-title-tab');
  const descEl = document.getElementById('compat-desc-tab');

  if (scoreEl) scoreEl.textContent = item.score;
  if (titleEl) titleEl.textContent = item.title;
  if (descEl) descEl.textContent = item.desc;
}};

window.shareCompatibility = function() {{
  alert('🎉 [공유 링크 복사 완료] 초코와 친구 강아지의 케미 지수 카드가 인스타/카톡 공유용으로 복사되었습니다!');
}};

window.openViralModal = function() {{
  const modal = document.getElementById('modal-viral-mbti');
  if (modal) modal.classList.remove('hidden');
  if (window.lucide) lucide.createIcons();
}};

window.closeViralModal = function() {{
  const modal = document.getElementById('modal-viral-mbti');
  if (modal) modal.classList.add('hidden');
}};

window.shareToInstagram = function() {{
  alert('📋 [인스타그램 공유] 인스타 스토리에 공유할 수 있는 감성 카드가 복사되었습니다!');
}};

window.openDogTalkModal = function() {{
  const modal = document.getElementById('modal-dogtalk');
  if (modal) modal.classList.remove('hidden');
  if (window.lucide) lucide.createIcons();
}};

window.closeDogTalkModal = function() {{
  const modal = document.getElementById('modal-dogtalk');
  if (modal) modal.classList.add('hidden');
}};

window.requestWalkMate = function(name) {{
  alert(`🐕 [산책 신청 완료] ${{name}} 보호자님께 산책 번개 요청을 보냈습니다!`);
}};

// 5. 1km Radius Places & Refresh
window.changeRadius = function(km) {{
  selectedRadius = km;
  document.querySelectorAll('.radius-btn').forEach(b => {{
    b.classList.remove('active', 'bg-white', 'dark:bg-neutral-700', 'text-indigo-600', 'dark:text-indigo-400', 'shadow-sm');
    b.classList.add('text-gray-500', 'dark:text-gray-400');
  }});

  const activeBtn = document.getElementById(`radius-btn-${{km}}`);
  if (activeBtn) {{
    activeBtn.classList.add('active', 'bg-white', 'dark:bg-neutral-700', 'text-indigo-600', 'dark:text-indigo-400', 'shadow-sm');
    activeBtn.classList.remove('text-gray-500', 'dark:text-gray-400');
  }}

  refreshRadiusFeed();
}};

window.filterRadiusCategory = function(cat) {{
  selectedRadiusCategory = cat;
  document.querySelectorAll('.feed-cat').forEach(b => {{
    b.classList.remove('active', 'bg-indigo-50', 'dark:bg-indigo-950/60', 'text-indigo-600', 'dark:text-indigo-300', 'border-indigo-200', 'dark:border-indigo-900/50');
    b.classList.add('bg-gray-50', 'dark:bg-neutral-800', 'text-gray-600', 'dark:text-gray-400', 'border-gray-200', 'dark:border-neutral-700');
  }});

  if (event && event.target) {{
    event.target.classList.add('active', 'bg-indigo-50', 'dark:bg-indigo-950/60', 'text-indigo-600', 'dark:text-indigo-300', 'border-indigo-200', 'dark:border-indigo-900/50');
    event.target.classList.remove('bg-gray-50', 'dark:bg-neutral-800', 'text-gray-600', 'dark:text-gray-400', 'border-gray-200', 'dark:border-neutral-700');
  }}

  renderRadiusFeedList();
}};

window.refreshRadiusFeed = function() {{
  const icon = document.getElementById('icon-refresh');
  if (icon) icon.classList.add('animate-spin');

  const container = document.getElementById('radius-places-feed');
  if (container) {{
    container.innerHTML = `
      <div class="py-6 text-center text-xs text-indigo-600 dark:text-indigo-400 font-bold space-y-1">
        <div class="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p>반경 ${{selectedRadius}}km 내 최신 정보를 검색 중...</p>
      </div>
    `;
  }}

  setTimeout(() => {{
    if (icon) icon.classList.remove('animate-spin');
    renderRadiusFeedList();
  }}, 350);
}};

function renderRadiusFeedList() {{
  const container = document.getElementById('radius-places-feed');
  if (!container) return;

  let filtered = radiusDataset.filter(p => p.distKm <= selectedRadius);
  if (selectedRadiusCategory !== 'all') {{
    filtered = filtered.filter(p => p.category === selectedRadiusCategory);
  }}

  container.innerHTML = filtered.map(p => `
    <div class="p-3 bg-gray-50 dark:bg-neutral-800/60 rounded-xl border border-gray-100 dark:border-neutral-800 space-y-2">
      <div class="flex items-start justify-between">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-white dark:bg-neutral-700 flex items-center justify-center text-base shadow-sm">
            ${{p.icon}}
          </div>
          <div>
            <div class="flex items-center gap-1.5">
              <h4 class="font-bold text-xs text-gray-900 dark:text-gray-100">${{p.name}}</h4>
              <span class="text-[10px] text-amber-500 font-bold">${{p.rating}}</span>
            </div>
            <p class="text-[10px] text-gray-400"><b class="text-indigo-600 dark:text-indigo-400 font-bold">${{p.distanceStr}}</b> • ${{p.status}}</p>
          </div>
        </div>
      </div>
      <p class="text-[11px] text-gray-600 dark:text-gray-300 bg-white dark:bg-neutral-900/60 p-2 rounded-lg border border-gray-100 dark:border-neutral-800">
        ${{p.summary}}
      </p>
      <div class="flex gap-1.5 pt-0.5">
        <a href="tel:${{p.phone}}" class="flex-1 py-1.5 bg-white dark:bg-neutral-700 hover:bg-gray-100 text-gray-800 dark:text-gray-200 border rounded-lg text-center font-bold text-[10px] flex items-center justify-center gap-1">
          <i data-lucide="phone" class="w-3 h-3"></i>
          <span>전화</span>
        </a>
        <button onclick="openKakaoRoute('${{p.name}}', '')" class="flex-1 py-1.5 bg-[#FEE500] hover:bg-[#FADA0A] text-[#191919] rounded-lg text-center font-bold text-[10px] flex items-center justify-center gap-1 shadow-sm">
          <span>길찾기</span>
        </button>
      </div>
    </div>
  `).join('');

  if (window.lucide) lucide.createIcons();
}}

// 6. Kakao Map Modal Functions
window.openMapModal = function() {{
  const modal = document.getElementById('modal-pet-map');
  if (modal) modal.classList.remove('hidden');
  setTimeout(() => {{
    initKakaoMap();
    if (window.lucide) lucide.createIcons();
  }}, 150);
}};

window.closeMapModal = function() {{
  const modal = document.getElementById('modal-pet-map');
  if (modal) modal.classList.add('hidden');
}};

function initKakaoMap() {{
  const container = document.getElementById('kakao-map-container');
  if (!container) return;

  if (typeof kakao !== 'undefined' && kakao.maps) {{
    const options = {{ center: new kakao.maps.LatLng(37.498095, 127.027610), level: 4 }};
    const map = new kakao.maps.Map(container, options);
    const marker = new kakao.maps.Marker({{ position: new kakao.maps.LatLng(37.498095, 127.027610), map: map }});
    const infowindow = new kakao.maps.InfoWindow({{ content: '<div style="padding:4px 8px;font-size:11px;font-weight:bold;color:#4f46e5;">📍 내 위치 (초코네)</div>' }});
    infowindow.open(map, marker);
  }} else {{
    container.innerHTML = '<div class="w-full h-full flex items-center justify-center text-xs text-gray-400">카카오맵 로드 중...</div>';
  }}
}}

window.openKakaoRoute = function(name, address) {{
  window.open(`https://map.kakao.com/link/search/${{encodeURIComponent(name)}}`, '_blank');
}};

window.clickAd = function(type, title) {{
  if (type === 'insurance') {{
    alert('💰 [다이렉트 펫보험 비교] 초코(3세, 말티즈) 맞춤 보장 비교 견적 페이지로 이동합니다.');
  }}
}};

// 7. Doctor Chart
window.selectCheck = function(btn, category, value) {{
  const parent = btn.parentElement;
  parent.querySelectorAll('.check-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  if (category === 'appetite') currentSelectedAppetite = value;
  if (category === 'stool') currentSelectedStool = value;
}};

window.toggleMultiCheck = function(btn, symptom) {{
  btn.classList.toggle('active');
  if (btn.classList.contains('active')) {{
    if (!currentSelectedSymptoms.includes(symptom)) currentSelectedSymptoms.push(symptom);
  }} else {{
    currentSelectedSymptoms = currentSelectedSymptoms.filter(s => s !== symptom);
  }}
}};

window.saveHealthLog = function() {{
  const dateInput = document.getElementById('chart-date-input').value;
  const memoInput = document.getElementById('chart-memo-input').value.trim();
  const medMorning = document.getElementById('med-morning').checked;
  const medEvening = document.getElementById('med-evening').checked;

  const newLog = {{
    id: Date.now(),
    date: dateInput,
    appetite: currentSelectedAppetite,
    stool: currentSelectedStool,
    symptoms: [...currentSelectedSymptoms],
    medMorning: medMorning,
    medEvening: medEvening,
    memo: memoInput || '특이사항 없음'
  }};

  healthLogs.unshift(newLog);
  renderChartHistory();

  document.getElementById('chart-memo-input').value = '';
  document.getElementById('med-morning').checked = false;
  document.getElementById('med-evening').checked = false;
  document.querySelectorAll('#group-symptoms .symptom-btn').forEach(b => b.classList.remove('active'));
  currentSelectedSymptoms = [];

  alert('✅ 원장님 전송 차트에 오늘 기록이 안전하게 저장되었습니다!');
}};

function renderChartHistory() {{
  const container = document.getElementById('doctor-chart-history');
  const countEl = document.getElementById('chart-log-count');
  if (!container) return;

  if (countEl) countEl.textContent = `총 ${{healthLogs.length}}건`;

  container.innerHTML = healthLogs.map(log => `
    <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-3.5 space-y-2 shadow-sm">
      <div class="flex items-center justify-between border-b border-gray-100 dark:border-neutral-800 pb-2">
        <span class="font-bold text-xs text-gray-800 dark:text-gray-100">${{log.date}}</span>
        <div class="flex gap-1">
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-gray-100 dark:bg-neutral-800">식사: ${{log.appetite}}</span>
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-gray-100 dark:bg-neutral-800">배변: ${{log.stool}}</span>
        </div>
      </div>
      <p class="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">${{log.memo}}</p>
    </div>
  `).join('');

  if (window.lucide) lucide.createIcons();
}}

window.openSendModal = function() {{
  const modal = document.getElementById('modal-send-chart');
  if (modal) modal.classList.remove('hidden');
  if (window.lucide) lucide.createIcons();
}};

window.closeSendModal = function() {{
  const modal = document.getElementById('modal-send-chart');
  if (modal) modal.classList.add('hidden');
}};

window.executeHospitalSend = function(method) {{
  alert('🏥 [전송 완료] 지정 동물병원 EMR 전자차트로 최근 7일간의 차트가 안전하게 전송되었습니다!');
  closeSendModal();
}};

window.generateChartPDF = function() {{
  const element = document.getElementById('printable-pdf-chart');
  element.classList.remove('hidden');
  const opt = {{ margin: 10, filename: '스마트닥터차트.pdf', jsPDF: {{ unit: 'mm', format: 'a4', orientation: 'portrait' }} }};
  html2pdf().set(opt).from(element).save().then(() => {{
    element.classList.add('hidden');
    alert('📄 [PDF 다운로드 완료] 병원 제출용 차트가 발급되었습니다.');
  }});
}};
"""

# Write files
with open(os.path.join(APP_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html_content)

with open(os.path.join(APP_DIR, 'app.js'), 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Rebuilt index.html and app.js successfully with clean global bindings!")