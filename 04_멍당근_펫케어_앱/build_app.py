# App Builder Script
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. index.html
html_code = """<!DOCTYPE html>
<html lang="ko" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>펫로그 AI (PetLog AI) - 스마트 반려동물 헬스케어 & 병원 전송 차트</title>
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#eef2ff',
              100: '#e0e7ff',
              500: '#4f46e5',
              600: '#4338ca',
              700: '#3730a3',
            },
            meta: {
              dark: '#000000',
              card: '#121212',
              border: '#262626',
              textMuted: '#a8a8a8'
            }
          }
        }
      }
    }
  </script>

  <!-- Lucide Icons CDN -->
  <script src="https://unpkg.com/lucide@latest"></script>
  
  <!-- html2pdf.js for Doctor Chart Export -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>

  <!-- Custom Styles -->
  <link rel="stylesheet" href="style.css">
</head>
<body class="bg-gray-100 dark:bg-black text-gray-900 dark:text-gray-100 flex justify-center min-h-screen antialiased select-none">

  <!-- Mobile Frame Container (App Viewport) -->
  <div id="app-container" class="w-full max-w-md bg-white dark:bg-black min-h-screen shadow-2xl relative flex flex-col pb-20 overflow-x-hidden border-x border-gray-200 dark:border-neutral-900">
    
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
        <button id="btn-theme-toggle" onclick="toggleTheme()" class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800 text-gray-600 dark:text-gray-300" title="화면 테마 변경">
          <i data-lucide="sun" class="w-5 h-5 dark:hidden"></i>
          <i data-lucide="moon" class="w-5 h-5 hidden dark:block"></i>
        </button>
        <!-- Hospital Quick Share Header Button -->
        <button onclick="switchTab('chart')" class="flex items-center gap-1 px-2.5 py-1 bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-900/50 rounded-full text-xs font-semibold hover:scale-105 transition-transform">
          <i data-lucide="stethoscope" class="w-3.5 h-3.5"></i>
          <span>병원전송</span>
        </button>
      </div>
    </header>

    <!-- Main Content Dynamic View Container -->
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
              <p class="text-xs text-indigo-100 mt-0.5">최근 체중: 3.4kg | 정기검진 D-14</p>
              <div class="flex gap-2 mt-2">
                <span class="text-[11px] bg-emerald-400/20 text-emerald-200 border border-emerald-400/30 px-2 py-0.5 rounded-full font-medium flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> 오늘 건강 양호
                </span>
                <span class="text-[11px] bg-white/10 px-2 py-0.5 rounded-full text-indigo-100">
                  담당: 서울24시동물의료센터
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Daily Health Score & Briefing -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-1.5 font-bold text-sm text-indigo-600 dark:text-indigo-400">
              <i data-lucide="sparkles" class="w-4 h-4"></i>
              <span>AI 데일리 헬스 브리핑</span>
            </div>
            <span class="text-xs bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 font-bold px-2 py-0.5 rounded-full">건강지수 94점</span>
          </div>
          <p id="home-ai-briefing-text" class="text-xs leading-relaxed text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-neutral-800/60 p-3 rounded-xl border border-gray-100 dark:border-neutral-800">
            "초코의 최근 3일간 식사량과 활동량이 매우 안정적입니다. 단, 어제 저녁 산책 후 가려움증을 1회 체크하셨으니 발바닥 습진 여부를 관찰해주세요."
          </p>
          <div class="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-neutral-800 text-center">
            <div class="p-2 bg-gray-50 dark:bg-neutral-800/40 rounded-xl">
              <span class="text-[10px] text-gray-500">오늘 산책</span>
              <p class="text-sm font-bold text-gray-800 dark:text-gray-200 mt-0.5">38분 (1.8km)</p>
            </div>
            <div class="p-2 bg-gray-50 dark:bg-neutral-800/40 rounded-xl">
              <span class="text-[10px] text-gray-500">사료 섭취</span>
              <p class="text-sm font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">정상 (120g)</p>
            </div>
            <div class="p-2 bg-gray-50 dark:bg-neutral-800/40 rounded-xl">
              <span class="text-[10px] text-gray-500">물 음수량</span>
              <p class="text-sm font-bold text-blue-600 dark:text-blue-400 mt-0.5">250ml</p>
            </div>
          </div>
        </div>

        <!-- Quick 3-Second V-Check Banner -->
        <div onclick="switchTab('chart')" class="bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-2xl p-4 cursor-pointer shadow-md hover:opacity-95 transition-all flex items-center justify-between">
          <div class="space-y-1">
            <div class="flex items-center gap-1.5 text-xs font-bold bg-white/20 w-fit px-2 py-0.5 rounded-full">
              <i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i>
              <span>3초 스마트 V체크</span>
            </div>
            <h3 class="font-bold text-base">오늘 우리 아이 상태는 어떤가요?</h3>
            <p class="text-xs text-orange-100">체크된 기록은 원장님 전송 차트에 자동 누적됩니다.</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center shrink-0">
            <i data-lucide="chevron-right" class="w-6 h-6"></i>
          </div>
        </div>

        <!-- Quick Service Navigation (O2O) -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-sm text-gray-800 dark:text-gray-200">케어 & 픽업 매칭 서비스</h3>
            <button onclick="switchTab('services')" class="text-xs text-indigo-600 dark:text-indigo-400 font-semibold flex items-center gap-0.5">전체보기 <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i></button>
          </div>

          <div class="grid grid-cols-4 gap-2 text-center">
            <button onclick="openServiceTab('pickup')" class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 p-3 rounded-2xl hover:border-indigo-500 transition-all flex flex-col items-center gap-1.5">
              <div class="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center text-xl">
                🚗
              </div>
              <span class="text-xs font-bold">픽업 이동</span>
              <span class="text-[10px] text-gray-400">병원/미용실</span>
            </button>

            <button onclick="openServiceTab('education')" class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 p-3 rounded-2xl hover:border-indigo-500 transition-all flex flex-col items-center gap-1.5">
              <div class="w-10 h-10 rounded-xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center text-xl">
                🎓
              </div>
              <span class="text-xs font-bold">방문 교육</span>
              <span class="text-[10px] text-gray-400">행동 교정</span>
            </button>

            <button onclick="openServiceTab('care')" class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 p-3 rounded-2xl hover:border-indigo-500 transition-all flex flex-col items-center gap-1.5">
              <div class="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-xl">
                🏠
              </div>
              <span class="text-xs font-bold">방문 돌봄</span>
              <span class="text-[10px] text-gray-400">전문 시터</span>
            </button>

            <button onclick="openServiceTab('walk')" class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 p-3 rounded-2xl hover:border-indigo-500 transition-all flex flex-col items-center gap-1.5">
              <div class="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center text-xl">
                🦮
              </div>
              <span class="text-xs font-bold">산책 대행</span>
              <span class="text-[10px] text-gray-400">GPS 트래킹</span>
            </button>
          </div>
        </div>

        <!-- Recent Logs List Preview -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-sm flex items-center gap-1.5">
              <i data-lucide="clipboard-list" class="w-4 h-4 text-indigo-500"></i>
              <span>최근 차트 기록</span>
            </h3>
            <button onclick="switchTab('chart')" class="text-xs text-indigo-600 dark:text-indigo-400 font-semibold">기록 추가 +</button>
          </div>
          <div id="home-recent-logs" class="space-y-2 text-xs">
            <!-- Rendered by JS -->
          </div>
        </div>

      </section>

      <!-- ================= 2. DOCTOR CHART TAB (병원 전송용 스마트 차트) ================= -->
      <section id="view-chart" class="tab-view hidden p-4 space-y-4">
        
        <!-- Header Actions -->
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
            <button onclick="openSendModal()" class="flex-1 bg-white text-red-600 font-bold py-2.5 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-md hover:bg-rose-50 transition-all">
              <i data-lucide="send" class="w-4 h-4"></i>
              <span>원장님께 차트 전송 (PDF/링크)</span>
            </button>
            <button onclick="generateChartPDF()" class="bg-black/30 hover:bg-black/40 text-white font-semibold py-2.5 px-3 rounded-xl text-xs flex items-center justify-center gap-1">
              <i data-lucide="download" class="w-4 h-4"></i>
              <span>PDF</span>
            </button>
          </div>
        </div>

        <!-- Quick Input Form (3-Second V-Check) -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-4">
          <div class="flex items-center justify-between border-b border-gray-100 dark:border-neutral-800 pb-2">
            <div class="font-bold text-sm flex items-center gap-1.5 text-gray-800 dark:text-gray-100">
              <i data-lucide="check-square" class="w-4 h-4 text-emerald-500"></i>
              <span>오늘의 원터치 V-체크</span>
            </div>
            <input type="date" id="chart-date-input" class="text-xs bg-gray-100 dark:bg-neutral-800 border-none rounded-lg px-2 py-1 text-gray-700 dark:text-gray-200 font-medium">
          </div>

          <!-- 1. Appetite & Water -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-gray-600 dark:text-gray-400 flex items-center gap-1">
              <span>🍚 식사/식욕 상태</span>
            </label>
            <div class="grid grid-cols-4 gap-1.5" id="group-appetite">
              <button type="button" onclick="selectCheck(this, 'appetite', '정상')" class="check-btn active py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800">정상</button>
              <button type="button" onclick="selectCheck(this, 'appetite', '약간감소')" class="check-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800">약간감소</button>
              <button type="button" onclick="selectCheck(this, 'appetite', '거부(안먹음)')" class="check-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800 text-red-500">거부</button>
              <button type="button" onclick="selectCheck(this, 'appetite', '과식/폭식')" class="check-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800">과식</button>
            </div>
          </div>

          <!-- 2. Stool & Urine -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-gray-600 dark:text-gray-400 flex items-center gap-1">
              <span>💩 배변/배뇨 상태</span>
            </label>
            <div class="grid grid-cols-4 gap-1.5" id="group-stool">
              <button type="button" onclick="selectCheck(this, 'stool', '정상변')" class="check-btn active py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800">정상변</button>
              <button type="button" onclick="selectCheck(this, 'stool', '묽은변/설사')" class="check-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800 text-amber-500">설사</button>
              <button type="button" onclick="selectCheck(this, 'stool', '혈변/점액변')" class="check-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800 text-red-500">혈변</button>
              <button type="button" onclick="selectCheck(this, 'stool', '변비/미배변')" class="check-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800">변비</button>
            </div>
          </div>

          <!-- 3. Symptoms (Multiple Choices) -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-gray-600 dark:text-gray-400">⚠️ 이상 증상 (중복 선택 가능)</label>
            <div class="grid grid-cols-3 gap-1.5" id="group-symptoms">
              <button type="button" onclick="toggleMultiCheck(this, '구토')" class="symptom-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800">🤮 구토</button>
              <button type="button" onclick="toggleMultiCheck(this, '기침/쌕쌕거림')" class="symptom-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800">😮‍💨 기침/호흡</button>
              <button type="button" onclick="toggleMultiCheck(this, '가려움/긁음')" class="symptom-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800">🐾 가려움/긁음</button>
              <button type="button" onclick="toggleMultiCheck(this, '다리절음(파행)')" class="symptom-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800">🦵 다리절음</button>
              <button type="button" onclick="toggleMultiCheck(this, '기력저하/무기력')" class="symptom-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800">😴 기력저하</button>
              <button type="button" onclick="toggleMultiCheck(this, '눈물/눈곱')" class="symptom-btn py-2 text-xs rounded-xl border border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800">👀 눈물/눈곱</button>
            </div>
          </div>

          <!-- 4. Medication -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-gray-600 dark:text-gray-400">💊 투약/처치 기록</label>
            <div class="flex gap-2">
              <label class="flex items-center gap-1.5 text-xs bg-gray-50 dark:bg-neutral-800 px-3 py-2 rounded-xl border border-gray-200 dark:border-neutral-700 flex-1 cursor-pointer">
                <input type="checkbox" id="med-morning" class="rounded text-indigo-600">
                <span>아침 약 복용</span>
              </label>
              <label class="flex items-center gap-1.5 text-xs bg-gray-50 dark:bg-neutral-800 px-3 py-2 rounded-xl border border-gray-200 dark:border-neutral-700 flex-1 cursor-pointer">
                <input type="checkbox" id="med-evening" class="rounded text-indigo-600">
                <span>저녁 약 복용</span>
              </label>
            </div>
          </div>

          <!-- 5. Memo & Photo Upload -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold text-gray-600 dark:text-gray-400">📝 상세 메모 및 원장님께 전할 말</label>
            <textarea id="chart-memo-input" rows="2" placeholder="예: 오늘 아침 노란색 거품토 1회 발생. 산책 후 발을 계속 핥음" class="w-full text-xs p-3 rounded-xl bg-gray-50 dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 focus:outline-none focus:border-indigo-500"></textarea>
          </div>

          <!-- Save Log Button -->
          <button onclick="saveHealthLog()" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-md">
            <i data-lucide="plus-circle" class="w-4 h-4"></i>
            <span>차트에 오늘 기록 저장하기</span>
          </button>
        </div>

        <!-- History Timeline for Doctor Viewing -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-sm text-gray-800 dark:text-gray-200">누적 헬스케어 타임라인</h3>
            <span class="text-xs text-gray-400" id="chart-log-count">총 3건 기록됨</span>
          </div>
          <div id="doctor-chart-history" class="space-y-2.5">
            <!-- Rendered by JS -->
          </div>
        </div>

      </section>

      <!-- ================= 3. SERVICES (O2O 예약 & 요금) TAB ================= -->
      <section id="view-services" class="tab-view hidden p-4 space-y-4">
        
        <!-- Category Segment Buttons -->
        <div class="flex bg-gray-100 dark:bg-neutral-900 p-1 rounded-xl border border-gray-200 dark:border-neutral-800">
          <button onclick="switchServiceCategory('pickup')" id="subtab-pickup" class="service-subtab flex-1 py-2 text-xs font-bold rounded-lg bg-white dark:bg-neutral-800 shadow-sm text-indigo-600 dark:text-indigo-400 transition-all">픽업 이동</button>
          <button onclick="switchServiceCategory('education')" id="subtab-education" class="service-subtab flex-1 py-2 text-xs font-bold rounded-lg text-gray-500 hover:text-gray-900 dark:hover:text-gray-200 transition-all">전문 교육</button>
          <button onclick="switchServiceCategory('care')" id="subtab-care" class="service-subtab flex-1 py-2 text-xs font-bold rounded-lg text-gray-500 hover:text-gray-900 dark:hover:text-gray-200 transition-all">방문 돌봄</button>
          <button onclick="switchServiceCategory('walk')" id="subtab-walk" class="service-subtab flex-1 py-2 text-xs font-bold rounded-lg text-gray-500 hover:text-gray-900 dark:hover:text-gray-200 transition-all">산책 대행</button>
        </div>

        <!-- Dynamic Service Price & Selection Body -->
        <div id="service-detail-container" class="space-y-4">
          <!-- Dynamic Content rendered by switchServiceCategory -->
        </div>

        <!-- Service Region Coverage Accordion -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm">
          <div class="flex items-center justify-between cursor-pointer" onclick="toggleRegionList()">
            <div class="flex items-center gap-2">
              <i data-lucide="map-pin" class="w-4 h-4 text-indigo-500"></i>
              <span class="text-xs font-bold">전국 신청 가능 지역 안내</span>
            </div>
            <i id="region-chevron" data-lucide="chevron-down" class="w-4 h-4 text-gray-400 transition-transform"></i>
          </div>
          
          <div id="region-list-content" class="hidden mt-3 pt-3 border-t border-gray-100 dark:border-neutral-800 space-y-2 text-xs text-gray-600 dark:text-gray-300">
            <div class="p-2.5 bg-gray-50 dark:bg-neutral-800/50 rounded-xl">
              <span class="font-bold text-gray-800 dark:text-gray-100">📍 서울특별시 전체:</span>
              <p class="text-[11px] text-gray-500 mt-0.5">강남구, 서초구, 송파구, 마포구, 용산구 등 25개 전 자치구</p>
            </div>
            <div class="p-2.5 bg-gray-50 dark:bg-neutral-800/50 rounded-xl">
              <span class="font-bold text-gray-800 dark:text-gray-100">📍 경기도 & 인천:</span>
              <p class="text-[11px] text-gray-500 mt-0.5">성남시(분당), 고양시(일산), 수원시, 용인시, 하남시, 인천 전지역</p>
            </div>
            <div class="p-2.5 bg-gray-50 dark:bg-neutral-800/50 rounded-xl">
              <span class="font-bold text-gray-800 dark:text-gray-100">📍 주요 광역시:</span>
              <p class="text-[11px] text-gray-500 mt-0.5">부산, 대구, 대전, 광주, 울산, 세종특별자치시</p>
            </div>
          </div>
        </div>

      </section>

      <!-- ================= 4. AI CARE & SCANNER TAB ================= -->
      <section id="view-ai" class="tab-view hidden p-4 space-y-4">
        
        <div class="bg-gradient-to-br from-violet-600 to-indigo-800 rounded-2xl p-4 text-white shadow-lg space-y-2">
          <div class="flex items-center gap-2">
            <div class="p-2 bg-white/20 rounded-xl text-xl">✨</div>
            <div>
              <h2 class="text-base font-bold">AI 비전 건강 스캐너</h2>
              <p class="text-xs text-violet-100">사진 1장으로 피부·안구·대변 질환 사전 판별</p>
            </div>
          </div>
        </div>

        <!-- AI Image Upload & Scan Simulation -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-3">
          <h3 class="text-xs font-bold text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
            <i data-lucide="camera" class="w-4 h-4 text-indigo-500"></i>
            <span>진단할 부위 사진을 업로드하세요</span>
          </h3>

          <div id="ai-dropzone" onclick="triggerAIScan()" class="border-2 border-dashed border-gray-300 dark:border-neutral-700 rounded-2xl p-6 text-center cursor-pointer hover:border-indigo-500 transition-colors bg-gray-50 dark:bg-neutral-800/40">
            <div class="w-12 h-12 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 mx-auto flex items-center justify-center text-2xl mb-2">
              📸
            </div>
            <p class="text-xs font-bold text-gray-800 dark:text-gray-200">사진 촬영 또는 갤러리 선택</p>
            <p class="text-[11px] text-gray-400 mt-1">대변, 피부 붉은 반점, 눈물 자국, 귀 안쪽 등</p>
          </div>

          <!-- AI Result Box (Hidden by default) -->
          <div id="ai-result-box" class="hidden space-y-3 pt-2">
            <div class="p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/50 rounded-xl space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-amber-700 dark:text-amber-300 flex items-center gap-1">
                  <i data-lucide="alert-triangle" class="w-3.5 h-3.5"></i>
                  <span>AI 분석 결과: 경미한 지루성 피부염 의심 (일치율 88%)</span>
                </span>
                <span class="text-[10px] bg-amber-200 dark:bg-amber-900 text-amber-800 dark:text-amber-200 px-1.5 py-0.5 rounded font-bold">주의</span>
              </div>
              <p class="text-[11px] text-amber-900 dark:text-amber-200 leading-relaxed">
                붉은 반점과 각질 패턴이 관찰됩니다. 습식 목욕 후 건조를 철저히 해주시고, 긁는 행동이 2일 이상 지속되면 동물병원에서 세균/곰팡이 도말 검사를 권장합니다.
              </p>
            </div>
            <button onclick="addAIResultToChart()" class="w-full py-2.5 bg-gray-900 dark:bg-white text-white dark:text-black rounded-xl text-xs font-bold flex items-center justify-center gap-1.5">
              <i data-lucide="save" class="w-3.5 h-3.5"></i>
              <span>이 분석 결과를 닥터 차트에 자동 기록</span>
            </button>
          </div>
        </div>

        <!-- AI Voice/Bark Translator -->
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

      <!-- ================= 5. SETTINGS & META UI TAB (인스타그램/메타 완벽 구현) ================= -->
      <section id="view-settings" class="tab-view hidden p-2 space-y-1">
        
        <!-- Meta Style Account Center -->
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
                <p class="text-[11px] text-gray-500">비밀번호, 보안, 개인정보, 광고 기본 설정</p>
              </div>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </div>
        </div>

        <!-- Instagram/Meta Exact Settings Menu List -->
        <div class="space-y-0.5 text-sm">
          
          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="user-plus" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>친구 팔로우 및 초대</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="bell" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>알림</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="bookmark" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>저장됨 (북마크)</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="heart" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>좋아요</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="archive" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>보관 (스토리/피드 아카이브)</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="lock" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>개인정보 보호</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="sliders-horizontal" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>콘텐츠 기본 설정</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="user-check" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>계정 상태</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="share-2" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>프로필 간 공유</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="sparkles" class="w-5 h-5 text-indigo-500"></i>
              <span class="font-semibold text-indigo-600 dark:text-indigo-400">Meta AI 지원 어시스턴트</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="help-circle" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>도움말 및 고객센터</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
          </button>

          <button class="settings-item w-full flex items-center justify-between p-3.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
            <div class="flex items-center gap-3">
              <i data-lucide="info" class="w-5 h-5 text-gray-700 dark:text-gray-300"></i>
              <span>앱 정보 및 버전 (v2.4.0)</span>
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

      <button onclick="switchTab('chart')" id="nav-chart" class="nav-btn flex flex-col items-center gap-1 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex-1 py-1">
        <div class="relative">
          <i data-lucide="clipboard-pen" class="w-5 h-5"></i>
          <span class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-red-500"></span>
        </div>
        <span class="text-[10px] font-bold">닥터차트</span>
      </button>

      <button onclick="switchTab('services')" id="nav-services" class="nav-btn flex flex-col items-center gap-1 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex-1 py-1">
        <i data-lucide="truck" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">케어/픽업</span>
      </button>

      <button onclick="switchTab('ai')" id="nav-ai" class="nav-btn flex flex-col items-center gap-1 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex-1 py-1">
        <i data-lucide="sparkles" class="w-5 h-5 text-violet-500"></i>
        <span class="text-[10px] font-bold">AI진단</span>
      </button>

      <button onclick="switchTab('settings')" id="nav-settings" class="nav-btn flex flex-col items-center gap-1 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex-1 py-1">
        <i data-lucide="settings" class="w-5 h-5"></i>
        <span class="text-[10px] font-bold">설정</span>
      </button>

    </nav>

    <!-- Modal: Send Doctor Chart to Veterinary Clinic -->
    <div id="modal-send-chart" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-end sm:items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-md bg-white dark:bg-neutral-900 rounded-t-3xl sm:rounded-3xl p-5 space-y-4 max-h-[85vh] overflow-y-auto border border-gray-200 dark:border-neutral-800 animate-slide-up">
        
        <div class="flex items-center justify-between border-b border-gray-100 dark:border-neutral-800 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-xl">🩺</span>
            <h3 class="font-bold text-base">동물병원 원장님께 전송하기</h3>
          </div>
          <button onclick="closeSendModal()" class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>

        <!-- AI Clinical 3-Line Summary Card -->
        <div class="bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-900/50 rounded-2xl p-3.5 space-y-1.5">
          <div class="flex items-center gap-1.5 text-xs font-bold text-indigo-700 dark:text-indigo-300">
            <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
            <span>AI 사전 문진 3줄 요약 (진료 보조용)</span>
          </div>
          <ul id="ai-modal-summary-list" class="text-xs space-y-1 text-indigo-950 dark:text-indigo-200 leading-relaxed list-disc list-inside">
            <li>최근 3일간 식욕 정상 범위 유지 (오늘 1회 약간 감소 기록)</li>
            <li>주요 이상 증상: 09/17 노란 거품토 1회, 발바닥 가려움증 2회 호소</li>
            <li>투약 현황: 심장사상충 예방 완료, 처방약 복용 완료</li>
          </ul>
        </div>

        <!-- Hospital Destination Picker -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-gray-700 dark:text-gray-300">전송할 동물병원 선택</label>
          <select id="hospital-select" class="w-full text-xs p-3 rounded-xl bg-gray-50 dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700">
            <option value="seoul24">📍 서울24시 동물의료센터 (원장: 김진우 수의사)</option>
            <option value="gangnam_vet">📍 강남 펫종합병원 (원장: 이서연 수의사)</option>
            <option value="bundang_vet">📍 분당 바른동물병원 (원장: 박민수 수의사)</option>
            <option value="custom">직접 카카오톡 / 링크로 전달하기</option>
          </select>
        </div>

        <!-- Transfer Actions -->
        <div class="space-y-2 pt-2">
          <button onclick="executeHospitalSend('direct')" class="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-red-600/30">
            <i data-lucide="send" class="w-4 h-4"></i>
            <span>지정 병원 EMR 전자차트로 즉시 전송</span>
          </button>
          <div class="flex gap-2">
            <button onclick="executeHospitalSend('kakao')" class="flex-1 py-2.5 bg-[#FEE500] text-[#191919] font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow">
              <span>💬 카카오톡 전송</span>
            </button>
            <button onclick="executeHospitalSend('link')" class="flex-1 py-2.5 bg-gray-100 dark:bg-neutral-800 text-gray-800 dark:text-gray-200 font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 border border-gray-200 dark:border-neutral-700">
              <i data-lucide="link" class="w-3.5 h-3.5"></i>
              <span>웹 열람 링크 복사</span>
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- Hidden Printable Doctor Report DOM for PDF Export -->
    <div id="printable-pdf-chart" class="hidden p-8 bg-white text-black font-sans">
      <div class="border-b-2 border-indigo-600 pb-4 mb-4 flex justify-between items-start">
        <div>
          <h1 class="text-2xl font-black text-indigo-700">🐾 스마트 펫 헬스케어 차트 (임상 보고서)</h1>
          <p class="text-xs text-gray-500 mt-1">발급일시: <span id="pdf-export-date"></span> | 서비스: 펫로그 AI</p>
        </div>
        <div class="text-right text-xs">
          <p class="font-bold text-gray-800">환축명: 초코 (말티즈, 3세, 3.4kg)</p>
          <p class="text-gray-600">보호자: 김태형 (010-****-5678)</p>
        </div>
      </div>

      <div class="bg-indigo-50 p-4 rounded-lg mb-6 border border-indigo-100">
        <h3 class="font-bold text-sm text-indigo-900 mb-2">📋 AI 사전 임상 요약</h3>
        <p class="text-xs text-indigo-950 leading-relaxed" id="pdf-ai-summary">
          - 최근 7일간의 기록 취합 결과: 식욕 전반적 양호(1회 일시적 저하), 배변 정상.<br>
          - 특이 소견: 9월 17일 노란 거품토 1회 및 발바닥 소양증 관찰.<br>
          - 약물: 정기 심장사상충 투약 완료.
        </p>
      </div>

      <h3 class="font-bold text-sm mb-3 border-l-4 border-indigo-600 pl-2">📅 일자별 홈케어 상세 기록표</h3>
      <table class="w-full text-xs text-left border-collapse border border-gray-300">
        <thead>
          <tr class="bg-gray-100 border-b border-gray-300 text-gray-700">
            <th class="p-2 border border-gray-300">일자</th>
            <th class="p-2 border border-gray-300">식욕/식사</th>
            <th class="p-2 border border-gray-300">배변/소변</th>
            <th class="p-2 border border-gray-300">이상 증상</th>
            <th class="p-2 border border-gray-300">투약</th>
            <th class="p-2 border border-gray-300">보호자 메모</th>
          </tr>
        </thead>
        <tbody id="pdf-table-body">
          <!-- Rendered in JS -->
        </tbody>
      </table>
    </div>

  </div>

  <!-- Custom Scripts -->
  <script src="app.js"></script>
</body>
</html>
"""

# 2. style.css
css_code = """/* PetLog AI Custom CSS */
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&display=swap');

body {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
  -webkit-tap-highlight-color: transparent;
}

::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(150, 150, 150, 0.3);
  border-radius: 4px;
}

.check-btn.active {
  background-color: #4f46e5 !important;
  color: #ffffff !important;
  border-color: #4f46e5 !important;
  font-weight: bold;
}

.symptom-btn.active {
  background-color: #ef4444 !important;
  color: #ffffff !important;
  border-color: #ef4444 !important;
  font-weight: bold;
}

.service-subtab.active {
  background-color: #ffffff !important;
  color: #4f46e5 !important;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.dark .service-subtab.active {
  background-color: #262626 !important;
  color: #818cf8 !important;
}

.nav-btn.active {
  color: #4f46e5 !important;
}

.dark .nav-btn.active {
  color: #818cf8 !important;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-up {
  animation: slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
"""

# 3. app.js
js_code = """// PetLog AI Main Application Logic

let healthLogs = [
  {
    id: 1,
    date: '2026-09-18',
    appetite: '정상',
    stool: '정상변',
    symptoms: [],
    medMorning: true,
    medEvening: false,
    memo: '아침 사료 완식. 산책 38분 기분 좋게 완료함.'
  },
  {
    id: 2,
    date: '2026-09-17',
    appetite: '약간감소',
    stool: '묽은변/설사',
    symptoms: ['구토', '가려움/긁음'],
    medMorning: true,
    medEvening: true,
    memo: '새벽 6시경 노란색 거품토 1회. 오른쪽 뒷발바닥을 계속 핥고 긁음.'
  },
  {
    id: 3,
    date: '2026-09-16',
    appetite: '정상',
    stool: '정상변',
    symptoms: ['눈물/눈곱'],
    medMorning: true,
    medEvening: true,
    memo: '눈 주변 눈물 자국이 조금 심해져서 전용 세정제로 닦아줌.'
  }
];

let currentSelectedAppetite = '정상';
let currentSelectedStool = '정상변';
let currentSelectedSymptoms = [];
let currentServiceTab = 'pickup';
let selectedPickupMinutes = 30;
let selectedPetType = 'small_dog';

document.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  
  const today = new Date().toISOString().split('T')[0];
  const dateInput = document.getElementById('chart-date-input');
  if (dateInput) dateInput.value = today;

  renderRecentLogs();
  renderChartHistory();
  renderServiceDetail();
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

function toggleTheme() {
  const html = document.documentElement;
  if (html.classList.contains('dark')) {
    html.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  } else {
    html.classList.add('dark');
    localStorage.setItem('theme', 'dark');
  }
}

function switchTab(tabId) {
  const tabs = ['home', 'chart', 'services', 'ai', 'settings'];
  const titles = {
    home: '펫로그 AI',
    chart: '스마트 닥터 차트',
    services: '케어 & 픽업 예약',
    ai: 'AI 건강 스캐너',
    settings: '설정'
  };

  tabs.forEach(t => {
    const view = document.getElementById(`view-${t}`);
    const nav = document.getElementById(`nav-${t}`);
    if (t === tabId) {
      if (view) view.classList.remove('hidden');
      if (nav) {
        nav.classList.add('active');
        nav.classList.remove('text-gray-400');
      }
    } else {
      if (view) view.classList.add('hidden');
      if (nav) {
        nav.classList.remove('active');
        nav.classList.add('text-gray-400');
      }
    }
  });

  const headerTitle = document.getElementById('header-title');
  const backNav = document.getElementById('btn-back-nav');
  if (headerTitle) headerTitle.textContent = titles[tabId] || '펫로그 AI';
  if (backNav) {
    if (tabId !== 'home') backNav.classList.remove('hidden');
    else backNav.classList.add('hidden');
  }

  lucide.createIcons();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function openServiceTab(subType) {
  switchTab('services');
  switchServiceCategory(subType);
}

function selectCheck(btn, category, value) {
  const parent = btn.parentElement;
  parent.querySelectorAll('.check-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  if (category === 'appetite') currentSelectedAppetite = value;
  if (category === 'stool') currentSelectedStool = value;
}

function toggleMultiCheck(btn, symptom) {
  btn.classList.toggle('active');
  if (btn.classList.contains('active')) {
    if (!currentSelectedSymptoms.includes(symptom)) {
      currentSelectedSymptoms.push(symptom);
    }
  } else {
    currentSelectedSymptoms = currentSelectedSymptoms.filter(s => s !== symptom);
  }
}

function saveHealthLog() {
  const dateInput = document.getElementById('chart-date-input').value;
  const memoInput = document.getElementById('chart-memo-input').value.trim();
  const medMorning = document.getElementById('med-morning').checked;
  const medEvening = document.getElementById('med-evening').checked;

  const newLog = {
    id: Date.now(),
    date: dateInput,
    appetite: currentSelectedAppetite,
    stool: currentSelectedStool,
    symptoms: [...currentSelectedSymptoms],
    medMorning: medMorning,
    medEvening: medEvening,
    memo: memoInput || '특이사항 없음'
  };

  healthLogs.unshift(newLog);
  renderRecentLogs();
  renderChartHistory();

  document.getElementById('chart-memo-input').value = '';
  document.getElementById('med-morning').checked = false;
  document.getElementById('med-evening').checked = false;
  document.querySelectorAll('#group-symptoms .symptom-btn').forEach(b => b.classList.remove('active'));
  currentSelectedSymptoms = [];

  alert('✅ 원장님 전송 차트에 오늘 기록이 안전하게 저장되었습니다!');
}

function renderRecentLogs() {
  const container = document.getElementById('home-recent-logs');
  if (!container) return;
  
  if (healthLogs.length === 0) {
    container.innerHTML = '<p class="text-gray-400 text-center py-2">기록된 차트가 없습니다.</p>';
    return;
  }

  container.innerHTML = healthLogs.slice(0, 3).map(log => `
    <div class="p-2.5 rounded-xl bg-gray-50 dark:bg-neutral-800/60 border border-gray-100 dark:border-neutral-800 flex items-start justify-between">
      <div class="space-y-0.5">
        <div class="flex items-center gap-1.5">
          <span class="font-bold text-gray-800 dark:text-gray-200">${log.date}</span>
          <span class="px-1.5 py-0.2 rounded text-[10px] bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-semibold">${log.appetite}</span>
          <span class="px-1.5 py-0.2 rounded text-[10px] bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-semibold">${log.stool}</span>
        </div>
        <p class="text-[11px] text-gray-600 dark:text-gray-400 line-clamp-1">${log.memo}</p>
      </div>
      ${log.symptoms.length > 0 ? `
        <span class="text-[10px] bg-red-100 dark:bg-red-950 text-red-600 dark:text-red-400 px-1.5 py-0.5 rounded font-bold shrink-0">
          ⚠️ ${log.symptoms[0]}
        </span>
      ` : '<span class="text-[10px] text-emerald-500 font-bold">정상</span>'}
    </div>
  `).join('');
}

function renderChartHistory() {
  const container = document.getElementById('doctor-chart-history');
  const countEl = document.getElementById('chart-log-count');
  if (!container) return;

  if (countEl) countEl.textContent = `총 ${healthLogs.length}건 기록됨`;

  container.innerHTML = healthLogs.map(log => `
    <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-3.5 space-y-2 shadow-sm">
      <div class="flex items-center justify-between border-b border-gray-100 dark:border-neutral-800 pb-2">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full ${log.symptoms.length > 0 ? 'bg-red-500 animate-ping' : 'bg-emerald-500'}"></span>
          <span class="font-bold text-xs text-gray-800 dark:text-gray-100">${log.date}</span>
        </div>
        <div class="flex gap-1">
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-gray-100 dark:bg-neutral-800 text-gray-600 dark:text-gray-300">식사: ${log.appetite}</span>
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-gray-100 dark:bg-neutral-800 text-gray-600 dark:text-gray-300">배변: ${log.stool}</span>
        </div>
      </div>

      ${log.symptoms.length > 0 ? `
        <div class="flex flex-wrap gap-1">
          ${log.symptoms.map(s => `
            <span class="text-[10px] bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-900/40 text-red-600 dark:text-red-400 px-2 py-0.5 rounded-md font-bold">
              ⚠️ ${s}
            </span>
          `).join('')}
        </div>
      ` : ''}

      <p class="text-xs text-gray-700 dark:text-gray-300 leading-relaxed bg-gray-50 dark:bg-neutral-800/40 p-2.5 rounded-xl">
        ${log.memo}
      </p>

      <div class="flex items-center justify-between text-[10px] text-gray-400 pt-1">
        <span>💊 투약: ${log.medMorning ? '아침(O) ' : '아침(X) '}${log.medEvening ? '저녁(O)' : '저녁(X)'}</span>
        <button onclick="deleteLog(${log.id})" class="text-red-400 hover:text-red-600">삭제</button>
      </div>
    </div>
  `).join('');
  lucide.createIcons();
}

function deleteLog(id) {
  if (confirm('이 기록을 삭제하시겠습니까?')) {
    healthLogs = healthLogs.filter(l => l.id !== id);
    renderRecentLogs();
    renderChartHistory();
  }
}

function switchServiceCategory(category) {
  currentServiceTab = category;
  document.querySelectorAll('.service-subtab').forEach(b => b.classList.remove('active'));
  const activeBtn = document.getElementById(`subtab-${category}`);
  if (activeBtn) activeBtn.classList.add('active');
  renderServiceDetail();
}

function renderServiceDetail() {
  const container = document.getElementById('service-detail-container');
  if (!container) return;

  if (currentServiceTab === 'pickup') {
    container.innerHTML = `
      <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 space-y-4 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-bold text-sm">픽업 이용 시간 선택</h3>
            <p class="text-[11px] text-gray-400">서비스 수수료 별도</p>
          </div>
          <span class="text-xs font-bold text-indigo-600 dark:text-indigo-400">실시간 매칭 가능</span>
        </div>

        <div class="grid grid-cols-3 gap-2">
          ${[30, 60, 90, 120, 150, 180].map(mins => `
            <button onclick="selectPickupTime(${mins})" class="py-2.5 rounded-xl border text-xs font-bold transition-all ${selectedPickupMinutes === mins ? 'bg-indigo-600 text-white border-indigo-600 shadow' : 'bg-gray-50 dark:bg-neutral-800 border-gray-200 dark:border-neutral-700 text-gray-700 dark:text-gray-300'}">
              ${mins}분
            </button>
          `).join('')}
        </div>

        <div class="border-t border-gray-100 dark:border-neutral-800 pt-3 space-y-2">
          <h4 class="text-xs font-bold text-gray-700 dark:text-gray-300">픽업 ${selectedPickupMinutes}분 기본 요금</h4>
          
          <div class="space-y-2">
            <div onclick="selectPetType('cat')" class="p-3 rounded-xl border flex items-center justify-between cursor-pointer ${selectedPetType === 'cat' ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/20' : 'border-gray-200 dark:border-neutral-800'}">
              <div class="flex items-center gap-2">
                <span class="text-lg">🐱</span>
                <div>
                  <p class="text-xs font-bold">고양이</p>
                  <p class="text-[10px] text-gray-400">무게 상관없음</p>
                </div>
              </div>
              <span class="text-sm font-black text-indigo-600 dark:text-indigo-400">${(19500 * (selectedPickupMinutes / 30)).toLocaleString()}원</span>
            </div>

            <div onclick="selectPetType('small_dog')" class="p-3 rounded-xl border flex items-center justify-between cursor-pointer ${selectedPetType === 'small_dog' ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/20' : 'border-gray-200 dark:border-neutral-800'}">
              <div class="flex items-center gap-2">
                <span class="text-lg">🐕</span>
                <div>
                  <p class="text-xs font-bold">소 • 중형견</p>
                  <p class="text-[10px] text-gray-400">15kg 미만</p>
                </div>
              </div>
              <span class="text-sm font-black text-indigo-600 dark:text-indigo-400">${(19500 * (selectedPickupMinutes / 30)).toLocaleString()}원</span>
            </div>

            <div onclick="selectPetType('large_dog')" class="p-3 rounded-xl border flex items-center justify-between cursor-pointer ${selectedPetType === 'large_dog' ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/20' : 'border-gray-200 dark:border-neutral-800'}">
              <div class="flex items-center gap-2">
                <span class="text-lg">🦮</span>
                <div>
                  <p class="text-xs font-bold">대형견</p>
                  <p class="text-[10px] text-gray-400">15kg 이상</p>
                </div>
              </div>
              <span class="text-sm font-black text-indigo-600 dark:text-indigo-400">${(25000 * (selectedPickupMinutes / 30)).toLocaleString()}원</span>
            </div>
          </div>
        </div>

        <div class="bg-gray-50 dark:bg-neutral-800/60 rounded-xl p-3 space-y-1 text-xs text-gray-600 dark:text-gray-300">
          <div class="font-bold flex items-center gap-1 text-indigo-600 dark:text-indigo-400">
            <i data-lucide="check-circle" class="w-3.5 h-3.5"></i>
            <span>픽업 이동 서비스는 이럴 때 이용하세요</span>
          </div>
          <ul class="text-[11px] space-y-0.5 text-gray-500 list-disc list-inside">
            <li>동물병원 진료 및 정기검진 이동이 필요할 때</li>
            <li>반려동물 전용 미용실 예약 방문할 때</li>
            <li>애견 유치원 등원/하원이 바쁠 때</li>
          </ul>
        </div>

        <button onclick="bookService('픽업 이동')" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-md">
          <i data-lucide="calendar" class="w-4 h-4"></i>
          <span>픽업 드라이버 매칭 예약하기</span>
        </button>
      </div>
    `;
  } else if (currentServiceTab === 'education') {
    container.innerHTML = `
      <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 space-y-4 shadow-sm">
        <div class="flex gap-2">
          <button class="flex-1 py-2 rounded-xl bg-indigo-600 text-white text-xs font-bold">방문 교육</button>
          <button class="flex-1 py-2 rounded-xl bg-gray-100 dark:bg-neutral-800 text-gray-600 dark:text-gray-300 text-xs font-bold">영상/비대면 교육</button>
        </div>

        <div class="flex items-center justify-between border-b border-gray-100 dark:border-neutral-800 pb-3">
          <div>
            <h3 class="font-bold text-sm">전문 훈련사 방문 교육 (100분)</h3>
            <p class="text-[11px] text-gray-400">서비스 수수료 별도</p>
          </div>
          <span class="text-base font-black text-indigo-600 dark:text-indigo-400">150,000원</span>
        </div>

        <div class="space-y-2">
          <div class="p-3 bg-gray-50 dark:bg-neutral-800/60 rounded-xl space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-gray-800 dark:text-gray-200">1. 사전 상담 카드 분석</span>
              <i data-lucide="check" class="w-4 h-4 text-indigo-600"></i>
            </div>
            <p class="text-[11px] text-gray-500">교육 진행 전 생활 정보 및 행동 패턴을 사전 진단합니다.</p>
          </div>

          <div class="p-3 bg-gray-50 dark:bg-neutral-800/60 rounded-xl space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-gray-800 dark:text-gray-200">2. 현장 방문 맞춤 교정</span>
              <i data-lucide="check" class="w-4 h-4 text-indigo-600"></i>
            </div>
            <p class="text-[11px] text-gray-500">전문 훈련사가 자택으로 방문하여 문제 행동 원인을 즉시 교정합니다.</p>
          </div>

          <div class="p-3 bg-gray-50 dark:bg-neutral-800/60 rounded-xl space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-gray-800 dark:text-gray-200">3. 사후 솔루션 카드 발급</span>
              <i data-lucide="check" class="w-4 h-4 text-indigo-600"></i>
            </div>
            <p class="text-[11px] text-gray-500">가족 모두가 지켜야 할 일상 훈련 가이드 리포트를 앱으로 전달합니다.</p>
          </div>
        </div>

        <button onclick="bookService('방문 교육 100분')" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-md">
          <i data-lucide="user-check" class="w-4 h-4"></i>
          <span>전문 훈련사 배정 신청하기</span>
        </button>
      </div>
    `;
  } else if (currentServiceTab === 'care') {
    container.innerHTML = `
      <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 space-y-3 shadow-sm">
        <h3 class="font-bold text-sm">자택 방문 전문 펫시터 돌봄</h3>
        <p class="text-xs text-gray-500 leading-relaxed">혼자 있는 아이를 위해 검증된 펫시터가 방문하여 배변 정리, 식사 급여, 실내 놀이를 진행합니다.</p>
        <div class="p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/40 rounded-xl flex justify-between items-center">
          <span class="text-xs font-bold text-emerald-800 dark:text-emerald-200">기본 30분 케어</span>
          <span class="text-sm font-black text-emerald-600">22,000원~</span>
        </div>
        <button onclick="bookService('방문 돌봄')" class="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs">펫시터 예약하기</button>
      </div>
    `;
  } else if (currentServiceTab === 'walk') {
    container.innerHTML = `
      <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 space-y-3 shadow-sm">
        <h3 class="font-bold text-sm">전문 도그워커 1:1 산책 대행</h3>
        <p class="text-xs text-gray-500 leading-relaxed">실시간 GPS 경로 추적 및 배변 사진을 실시간으로 보호자님께 전송합니다.</p>
        <div class="p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/40 rounded-xl flex justify-between items-center">
          <span class="text-xs font-bold text-amber-800 dark:text-amber-200">30분 산책 (배변정리+발세척)</span>
          <span class="text-sm font-black text-amber-600">18,000원~</span>
        </div>
        <button onclick="bookService('산책 대행')" class="w-full py-3 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-xl text-xs">도그워커 예약하기</button>
      </div>
    `;
  }

  lucide.createIcons();
}

function selectPickupTime(minutes) {
  selectedPickupMinutes = minutes;
  renderServiceDetail();
}

function selectPetType(type) {
  selectedPetType = type;
  renderServiceDetail();
}

function toggleRegionList() {
  const content = document.getElementById('region-list-content');
  const chevron = document.getElementById('region-chevron');
  if (content.classList.contains('hidden')) {
    content.classList.remove('hidden');
    chevron.style.transform = 'rotate(180deg)';
  } else {
    content.classList.add('hidden');
    chevron.style.transform = 'rotate(0deg)';
  }
}

function bookService(serviceName) {
  alert(`🎉 [${serviceName}] 신청이 접수되었습니다! \\n담당 매니저가 5분 이내로 배정 및 연락드립니다.`);
}

function triggerAIScan() {
  const dropzone = document.getElementById('ai-dropzone');
  const resultBox = document.getElementById('ai-result-box');
  
  dropzone.innerHTML = `
    <div class="py-4 space-y-2">
      <div class="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p class="text-xs font-bold text-indigo-600 dark:text-indigo-400">Gemini 비전 AI 분석 중...</p>
      <p class="text-[10px] text-gray-400">피부 병변 및 염증 지수를 계산하고 있습니다.</p>
    </div>
  `;

  setTimeout(() => {
    dropzone.innerHTML = `
      <div class="text-center py-2">
        <span class="text-2xl">🔍</span>
        <p class="text-xs font-bold text-emerald-600">분석 완료 (재업로드 터치)</p>
      </div>
    `;
    resultBox.classList.remove('hidden');
    lucide.createIcons();
  }, 1200);
}

function addAIResultToChart() {
  const newLog = {
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    appetite: '정상',
    stool: '정상변',
    symptoms: ['가려움/긁음'],
    medMorning: true,
    medEvening: false,
    memo: '[AI 진단 자동 기록] 피부 발진 및 지루성 피부염 88% 의심 소견 기록됨.'
  };

  healthLogs.unshift(newLog);
  renderRecentLogs();
  renderChartHistory();
  alert('✅ AI 분석 결과가 닥터 차트에 성공적으로 반영되었습니다.');
  switchTab('chart');
}

function simulateVoiceAnalysis() {
  const btn = document.getElementById('btn-voice-record');
  const result = document.getElementById('voice-analysis-result');
  btn.innerHTML = '<span class="animate-pulse">🎙️ 5초간 소리를 듣고 있습니다...</span>';
  
  setTimeout(() => {
    btn.innerHTML = '<span>다시 녹음하기</span>';
    result.classList.remove('hidden');
    result.textContent = '🔊 분석 결과: "놀아줘요! 심심해요" (요구성 짖음 92%)';
  }, 2000);
}

function openSendModal() {
  const modal = document.getElementById('modal-send-chart');
  if (modal) modal.classList.remove('hidden');
  lucide.createIcons();
}

function closeSendModal() {
  const modal = document.getElementById('modal-send-chart');
  if (modal) modal.classList.add('hidden');
}

function executeHospitalSend(method) {
  const hospital = document.getElementById('hospital-select').value;
  let targetName = '지정 동물병원';
  if (hospital === 'seoul24') targetName = '서울24시 동물의료센터 (김진우 원장님)';
  else if (hospital === 'gangnam_vet') targetName = '강남 펫종합병원 (이서연 원장님)';
  else if (hospital === 'bundang_vet') targetName = '분당 바른동물병원 (박민수 원장님)';

  if (method === 'direct') {
    alert(`🏥 [전송 완료] \\n${targetName} 전자차트(EMR) 시스템으로 최근 7일간의 스마트 닥터 차트와 AI 사전 문진 요약이 안전하게 전송되었습니다!`);
    closeSendModal();
  } else if (method === 'kakao') {
    alert(`💬 카카오톡 알림톡으로 원장님 전용 열람 차트 카드가 발송되었습니다!`);
    closeSendModal();
  } else if (method === 'link') {
    navigator.clipboard.writeText('https://petlog.ai/chart/view?token=chocovet2026');
    alert(`🔗 원장님 전용 보안 열람 링크가 복사되었습니다! \\n(https://petlog.ai/chart/view?token=chocovet2026)`);
  }
}

function generateChartPDF() {
  const exportDate = document.getElementById('pdf-export-date');
  if (exportDate) exportDate.textContent = new Date().toLocaleString();

  const tableBody = document.getElementById('pdf-table-body');
  if (tableBody) {
    tableBody.innerHTML = healthLogs.map(l => `
      <tr class="border-b border-gray-200">
        <td class="p-2 border border-gray-300 font-bold">${l.date}</td>
        <td class="p-2 border border-gray-300">${l.appetite}</td>
        <td class="p-2 border border-gray-300">${l.stool}</td>
        <td class="p-2 border border-gray-300 text-red-600 font-bold">${l.symptoms.join(', ') || '없음'}</td>
        <td class="p-2 border border-gray-300">${l.medMorning ? '아침(O) ' : ''}${l.medEvening ? '저녁(O)' : ''}</td>
        <td class="p-2 border border-gray-300">${l.memo}</td>
      </tr>
    `).join('');
  }

  const element = document.getElementById('printable-pdf-chart');
  element.classList.remove('hidden');

  const opt = {
    margin: 10,
    filename: `펫로그AI_원장님차트_초코_${new Date().toISOString().split('T')[0]}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };

  html2pdf().set(opt).from(element).save().then(() => {
    element.classList.add('hidden');
    alert('📄 [PDF 발급 완료] 병원 제출용 스마트 닥터 차트 PDF가 다운로드되었습니다!');
  });
}
"""

# 4. manifest.json
manifest_code = """{
  "name": "펫로그 AI - 반려동물 스마트 닥터 차트 & 케어",
  "short_name": "펫로그 AI",
  "start_url": "./index.html",
  "display": "standalone",
  "background_color": "#000000",
  "theme_color": "#4f46e5",
  "icons": [
    {
      "src": "icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
"""

# 5. 실행 배치파일
bat_code = """@echo off
chcp 65001 > nul
echo ========================================================
echo  🐾 펫로그 AI (PetLog AI) 모바일 앱 실행 중...
echo ========================================================
echo.
echo [1] 로컬 웹서버를 시작하고 브라우저를 엽니다.
echo [2] 병원 전송 닥터 차트 / O2O 예약 / AI 진단 / 메타 설정
echo.

start "" "http://localhost:8088/index.html"
python -m http.server 8088
pause
"""

# 6. 구글플레이_출시_가이드.md
playstore_guide = """# 📱 『펫로그 AI (PetLog AI)』 구글 플레이스토어 출시 & ASO 가이드

## 1. 앱 스토어 등록 기본 정보
* **앱 이름 (30자 이내)**: `펫로그 AI - 반려동물 건강차트 & 펫케어`
* **간단한 설명 (80자 이내)**: `동물병원 원장님께 1초 전송하는 스마트 닥터 차트 & AI 건강 스캐너와 펫케어 예약`
* **자세한 설명**:
  - **3초 원터치 V-체크**: 식사, 음수량, 대변 상태, 이상 증상을 매일 간편 기록
  - **동물병원 원장님 전용 전송**: AI 3줄 사전 문진 요약 및 PDF 임상 리포트 원클릭 발송
  - **AI 비전 건강 스캐너**: 사진 한 장으로 피부염, 안구 질환, 배변 이상 사전 판별
  - **O2O 펫케어 매칭**: 픽업 이동(병원/미용실/유치원), 전문 훈련사 방문 교육, 도그워커 산책 대행
  - **다크모드 & 세련된 소셜 UI**: 메타/인스타그램 스타일의 깔끔한 사용자 경험

## 2. ASO (앱스토어 최적화) 핵심 키워드
`강아지 건강수첩`, `고양이 집사`, `동물병원 차트`, `반려견 다이어리`, `펫 헬스케어`, `펫시터`, `애견 훈련`, `펫 택시`, `도그워커`

## 3. APK / AAB 빌드 및 패키징 방법
1. **PWA to APK (Bubblewrap / TWA 활용)**:
   - 본 프로젝트의 `manifest.json`과 `index.html`을 기반으로 Google 공식 `bubblewrap` CLI를 사용하여 10분 만에 Android AAB 빌드 가능.
   - 명령어: `bubblewrap init --manifest=http://.../manifest.json` -> `bubblewrap build`
2. **Capacitor / Cordova 래핑**:
   - `npx cap init` -> `npx cap add android` -> Android Studio에서 서명된 APK/AAB 생성.
3. **Flutter 이식**:
   - 현재 구축된 UI 레이아웃과 데이터 모델 구조 그대로 Flutter 위젯으로 즉시 변환 가능.
"""

files = {
    'index.html': html_code,
    'style.css': css_code,
    'app.js': js_code,
    'manifest.json': manifest_code,
    '펫케어_앱_실행.bat': bat_code,
    '구글플레이_출시_가이드.md': playstore_guide
}

for filename, content in files.items():
    file_path = os.path.join(APP_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created: {filename}')

print('\\nAll PetCare App files generated successfully!')
