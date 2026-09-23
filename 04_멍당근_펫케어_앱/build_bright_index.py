import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"

bright_html = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>펫로그 AI (PetLog AI) - 1초 무료 AI 건강진단 & 멍냥궁합 & 스마트 차트</title>
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#eff6ff',
              100: '#dbeafe',
              500: '#3b82f6',
              600: '#2563eb',
              700: '#1d4ed8',
            },
            coral: {
              50: '#fff1f0',
              500: '#ff7e67',
              600: '#ea580c'
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

  <!-- Leaflet Map CSS/JS (Instant Real Map Engine Fallback) -->
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
  <div id="app-container" class="w-full max-w-md bg-white min-h-screen shadow-xl relative flex flex-col pb-28 overflow-x-hidden border-x border-slate-200/80">
    
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

    <!-- App Header (Wayo Style Bright Branding) -->
    <header class="px-5 py-3.5 flex items-center justify-between bg-white sticky top-8 z-30 border-b border-slate-50">
      <div class="flex items-center gap-2">
        <button id="btn-back-nav" onclick="switchTab('home')" class="hidden p-1 -ml-1 text-slate-700 hover:bg-slate-100 rounded-full">
          <i data-lucide="arrow-left" class="w-6 h-6"></i>
        </button>
        <div class="flex items-center gap-1.5">
          <span class="text-2xl animate-gentle">🐾</span>
          <h1 id="header-title" class="text-2xl font-black tracking-tight text-blue-600">petlog</h1>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <!-- Info Badge -->
        <button onclick="switchTab('settings')" class="flex items-center gap-1 px-2.5 py-1 bg-slate-50 hover:bg-slate-100 text-slate-600 rounded-full text-xs font-semibold border border-slate-200">
          <i data-lucide="info" class="w-3.5 h-3.5 text-blue-500"></i>
          <span>이용 안내</span>
        </button>
        <!-- Social Auth Login Button -->
        <button id="btn-header-auth" onclick="openAuthModal()" class="flex items-center gap-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-full text-xs font-bold shadow-sm transition-transform active:scale-95">
          <i data-lucide="log-in" class="w-3.5 h-3.5"></i>
          <span id="header-auth-label">로그인</span>
        </button>
      </div>
    </header>

    <!-- Main Content Container -->
    <main id="tab-content" class="flex-1 overflow-y-auto">

      <!-- ================= 1. HOME TAB (Wayo Bright Pastel Layout) ================= -->
      <section id="view-home" class="tab-view space-y-4 px-4 pt-2">
        
        <!-- Bright Welcome Title -->
        <div class="pt-1 px-1">
          <div class="flex items-center gap-2">
            <span class="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 font-bold">🐶 우리 아이 맞춤 케어</span>
            <span class="text-xs text-slate-400">말티즈 • 3세 초코</span>
          </div>
          <h2 class="text-2xl font-black text-slate-900 mt-1 leading-snug">
            초코와 함께하는<br><span class="text-blue-600">신나는 건강 케어 시간~</span> 🧸
          </h2>
        </div>

        <!-- Live Safe Streaming & Free Guarantee Pill Banner -->
        <div onclick="switchTab('ai')" class="bg-gradient-to-r from-blue-50 via-indigo-50 to-sky-50 border border-blue-200/80 rounded-2xl p-3.5 flex items-center justify-between shadow-sm cursor-pointer hover:border-blue-400 transition-all">
          <div class="flex items-center gap-2.5">
            <div class="w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping"></div>
            <span class="text-xs font-black text-slate-800">((•)) AI 1초 사진 건강 스캔으로 실시간 안심</span>
          </div>
          <span class="text-[11px] bg-blue-600 text-white px-2.5 py-0.5 rounded-full font-bold shadow-sm">
            100% 무료
          </span>
        </div>

        <!-- Membership Free Trial & Unlimited Pass Banner -->
        <div id="membership-tier-banner" onclick="openAuthModal()" class="bg-amber-50 border border-amber-200 rounded-2xl p-3 flex items-center justify-between cursor-pointer hover:border-amber-400 transition-all">
          <div class="flex items-center gap-2.5">
            <span class="text-2xl">🎁</span>
            <div>
              <div class="flex items-center gap-1.5">
                <span id="tier-badge-title" class="text-xs font-black text-amber-800">비회원 전 기능 1회 무료 체험권 적용 중</span>
              </div>
              <p id="tier-badge-desc" class="text-[11px] text-amber-700 mt-0.5">카카오/구글 1초 로그인 시 평생 무제한 무료 이용! ✨</p>
            </div>
          </div>
          <i data-lucide="chevron-right" class="w-4 h-4 text-amber-600"></i>
        </div>

        <!-- 2-Column Main Feature Cards (Wayo Style: 돌봄/산책 Layout) -->
        <div class="grid grid-cols-2 gap-3">
          
          <!-- Card 1: [BEST] AI 사진 건강 검진 -->
          <div onclick="switchTab('ai')" class="pet-card rounded-3xl p-4 flex flex-col justify-between h-48 cursor-pointer relative overflow-hidden bg-gradient-to-b from-blue-50/60 to-white hover:border-blue-300">
            <div class="flex items-start justify-between">
              <div>
                <span class="badge-best text-[10px] font-black px-2 py-0.5 rounded-full">BEST</span>
                <h3 class="text-base font-black text-slate-900 mt-2">AI 건강 검진</h3>
                <p class="text-[11px] text-slate-500 mt-0.5 leading-tight">사진 1장으로<br>피부•대변 판별</p>
              </div>
            </div>
            <div class="flex justify-end items-end">
              <div class="text-4xl transform hover:scale-110 transition-transform">
                🐕✨
              </div>
            </div>
          </div>

          <!-- Card 2: [HOT] 멍냥 궁합 & MBTI -->
          <div onclick="switchTab('compat')" class="pet-card rounded-3xl p-4 flex flex-col justify-between h-48 cursor-pointer relative overflow-hidden bg-gradient-to-b from-orange-50/60 to-white hover:border-orange-300">
            <div class="flex items-start justify-between">
              <div>
                <span class="badge-hot text-[10px] font-black px-2 py-0.5 rounded-full">HOT</span>
                <h3 class="text-base font-black text-slate-900 mt-2">멍냥 궁합</h3>
                <p class="text-[11px] text-slate-500 mt-0.5 leading-tight">친구와 케미 점수<br>& 음성 번역기</p>
              </div>
            </div>
            <div class="flex justify-end items-end">
              <div class="text-4xl transform hover:scale-110 transition-transform">
                🐈💕
              </div>
            </div>
          </div>

        </div>

        <!-- Full-Width Card: 🩺 스마트 닥터 차트 (원장님 전송) -->
        <div onclick="switchTab('chart')" class="pet-card rounded-3xl p-5 cursor-pointer bg-gradient-to-r from-blue-50/40 via-white to-indigo-50/40 hover:border-blue-400 relative overflow-hidden">
          <div class="flex items-center justify-between">
            <div class="space-y-1">
              <div class="flex items-center gap-1.5">
                <span class="text-[11px] font-black text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full">병원 원장님 전용</span>
                <span class="text-[10px] text-slate-400 font-semibold">1초 PDF 발송</span>
              </div>
              <h3 class="text-lg font-black text-slate-900">스마트 닥터 차트</h3>
              <p class="text-xs text-slate-500">매일 V-체크 기록하고 원장님 카카오톡으로 1초 전송</p>
            </div>
            <div class="w-16 h-16 rounded-2xl bg-blue-100 flex items-center justify-center text-3xl shadow-sm shrink-0">
              📋🩺
            </div>
          </div>
        </div>

        <!-- 3-Column Quick Services Icons (지도 / 픽업 / 훈련) -->
        <div class="bg-white rounded-3xl p-4 border border-slate-100 shadow-sm">
          <div class="flex items-center justify-between mb-3 px-1">
            <span class="text-xs font-black text-slate-800">🐾 빠른 펫 서비스 바로가기</span>
            <span class="text-[10px] text-slate-400">내 주변 1km</span>
          </div>
          <div class="grid grid-cols-3 gap-2 text-center">
            
            <div onclick="openMapModal()" class="p-2.5 rounded-2xl hover:bg-slate-50 cursor-pointer transition-colors">
              <div class="w-12 h-12 rounded-2xl bg-blue-50 mx-auto flex items-center justify-center text-2xl mb-1.5 shadow-sm">
                🗺️
              </div>
              <span class="text-xs font-bold text-slate-800 block">1km 펫지도</span>
              <span class="text-[10px] text-blue-600 font-semibold">24시 병원</span>
            </div>

            <div onclick="openProServiceModal('병원/미용실 안심 픽업 이동 서비스', '15,000원 ~', '🚗 전용 펫택시와 안전 켄넬을 갖춘 전문 드라이버의 1:1 왕복 픽업 서비스')" class="p-2.5 rounded-2xl hover:bg-slate-50 cursor-pointer transition-colors">
              <div class="w-12 h-12 rounded-2xl bg-amber-50 mx-auto flex items-center justify-center text-2xl mb-1.5 shadow-sm">
                🚗
              </div>
              <span class="text-xs font-bold text-slate-800 block">픽업 이동</span>
              <span class="text-[10px] text-amber-600 font-semibold">안심 예약</span>
            </div>

            <div onclick="openProServiceModal('1급 전문 훈련사 1:1 방문 맞춤 교육', '99,000원', '🎓 짖음, 분리불안, 배변훈련 전문 훈련사의 자택 방문 맞춤 솔루션')" class="p-2.5 rounded-2xl hover:bg-slate-50 cursor-pointer transition-colors">
              <div class="w-12 h-12 rounded-2xl bg-rose-50 mx-auto flex items-center justify-center text-2xl mb-1.5 shadow-sm">
                🎓
              </div>
              <span class="text-xs font-bold text-slate-800 block">방문 훈련</span>
              <span class="text-[10px] text-rose-600 font-semibold">1:1 코칭</span>
            </div>

          </div>
        </div>

        <!-- 👑 펫로그 PRO 유료 서비스 쇼케이스 -->
        <div class="bg-gradient-to-r from-slate-900 to-indigo-950 text-white rounded-3xl p-5 shadow-lg relative overflow-hidden">
          <div class="absolute -right-4 -bottom-4 opacity-10 text-8xl pointer-events-none">👑</div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-[11px] bg-amber-400 text-slate-950 font-black px-2.5 py-0.5 rounded-full">
              👑 펫로그 PRO 멤버십
            </span>
            <span class="text-[11px] text-amber-300 font-semibold">전문가 전용 케어</span>
          </div>
          <h3 class="text-base font-black text-white">24시 수의사 비대면 1:1 심층 상담</h3>
          <p class="text-xs text-slate-300 mt-0.5">정밀 진료가 필요한 응급 상황에 임상 수의사와 즉시 연결됩니다.</p>
          <div class="pt-3 flex gap-2">
            <button onclick="openProServiceModal('24시 수의사 1:1 비대면 상담', '29,000원', '🩺 전문 수의사의 임상 진단 소견서 및 처방 가이드 제공')" class="flex-1 py-2.5 bg-amber-400 hover:bg-amber-300 text-slate-950 font-black rounded-xl text-xs shadow">
              수의사 상담 신청 (29,000원)
            </button>
          </div>
        </div>

      </section>

      <!-- ================= 2. AI SCANNER TAB (무료 AI 건강 스캐너) ================= -->
      <section id="view-ai" class="tab-view hidden p-4 space-y-4">
        
        <div class="bg-gradient-to-br from-blue-600 via-indigo-600 to-violet-600 text-white rounded-3xl p-5 shadow-md relative overflow-hidden">
          <div class="flex items-center justify-between">
            <span class="text-xs bg-white/20 px-2.5 py-0.5 rounded-full font-bold">✨ Gemini 비전 AI 엔진</span>
            <span class="text-xs text-blue-100">100% 무료 판별</span>
          </div>
          <h3 class="text-xl font-black mt-2">📸 AI 1초 사진 건강 스캐너</h3>
          <p class="text-xs text-blue-100 mt-1">이상 부위(피부 붉은기, 귀 안쪽, 대변, 눈물 자국)를 촬영해 주세요.</p>
        </div>

        <!-- Camera Upload Box -->
        <div id="ai-dropzone" onclick="triggerAIScan()" class="border-2 border-dashed border-blue-300 hover:border-blue-500 rounded-3xl p-6 text-center cursor-pointer bg-blue-50/40 hover:bg-blue-50/70 transition-all space-y-2">
          <div class="w-16 h-16 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-3xl mx-auto shadow-inner">
            📷
          </div>
          <div>
            <p class="text-sm font-black text-slate-800">터치하여 사진 촬영 / 갤러리 업로드</p>
            <p class="text-xs text-slate-400 mt-0.5">JPG, PNG (비회원 1회 무료 / 회원 무제한 무료)</p>
          </div>
        </div>

        <!-- AI Result Box -->
        <div id="ai-result-box" class="hidden pet-card rounded-3xl p-5 space-y-3 border border-emerald-200 bg-emerald-50/30 animate-slide-up">
          <div class="flex items-center justify-between border-b border-emerald-200/60 pb-2">
            <div class="flex items-center gap-1.5">
              <span class="text-emerald-600 font-black text-sm">✅ AI 비전 정밀 분석 완료</span>
            </div>
            <span class="text-xs font-bold text-slate-500">신뢰도 96.4%</span>
          </div>

          <div class="space-y-2 text-xs">
            <div class="p-3 bg-white rounded-2xl border border-emerald-100 shadow-sm space-y-1">
              <div class="flex justify-between items-center font-bold">
                <span class="text-slate-800">🔍 의심 소견</span>
                <span class="text-rose-600 font-black">지루성 피부염 88%</span>
              </div>
              <p class="text-slate-600">피부 표면의 경미한 발적 및 각질이 관찰됩니다. 습도 조절과 저자극 약용 샴푸 관리를 권장합니다.</p>
            </div>

            <button onclick="addAIResultToChart()" class="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl shadow-sm text-xs flex items-center justify-center gap-1.5">
              <i data-lucide="plus-circle" class="w-4 h-4"></i>
              <span>이 분석 결과를 닥터 차트에 자동 기록하기</span>
            </button>
          </div>
        </div>

      </section>

      <!-- ================= 3. COMPATIBILITY & MBTI TAB (멍냥 궁합 & 음성 번역기) ================= -->
      <section id="view-compat" class="tab-view hidden p-4 space-y-4">
        
        <div class="bg-gradient-to-r from-rose-500 to-orange-500 text-white rounded-3xl p-5 shadow-md">
          <span class="text-xs bg-white/20 px-2.5 py-0.5 rounded-full font-bold">💖 멍냥 케미 분석실</span>
          <h3 class="text-xl font-black mt-2">반려견 성향 MBTI & 소통 번역</h3>
          <p class="text-xs text-rose-100 mt-1">우리 아이의 숨겨진 마음과 친구 댕댕이와의 궁합을 확인하세요!</p>
        </div>

        <!-- Voice Translator Card -->
        <div class="pet-card rounded-3xl p-5 space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-2xl">🎙️</span>
              <div>
                <h4 class="font-black text-sm text-slate-800">멍냥 음성/울음소리 AI 번역기</h4>
                <p class="text-[11px] text-slate-400">짖거나 낑낑대는 소리 주파수 해석</p>
              </div>
            </div>
          </div>

          <button id="btn-voice-record" onclick="simulateVoiceAnalysis()" class="w-full py-3 bg-rose-50 hover:bg-rose-100 text-rose-600 font-bold rounded-2xl border border-rose-200 text-xs flex items-center justify-center gap-2">
            <span>🎙️ 터치하여 5초간 소리 듣기</span>
          </button>

          <div id="voice-analysis-result" class="hidden p-3 bg-rose-50/50 rounded-2xl border border-rose-100 text-xs space-y-1">
            <p class="font-bold text-rose-700">🐾 AI 번역 결과: "지금 당장 산책 나가고 싶어요! 🐾"</p>
            <p class="text-slate-500 text-[11px]">흥분 지수 78% • 꼬리 흔듦 동반 • 간식 요구 소견</p>
          </div>
        </div>

        <!-- Compatibility Test Card -->
        <div class="pet-card rounded-3xl p-5 space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-2xl">💕</span>
              <div>
                <h4 class="font-black text-sm text-slate-800">친구 댕댕이와의 바이럴 궁합 테스트</h4>
                <p class="text-[11px] text-slate-400">산책 친구와 함께하는 케미 측정</p>
              </div>
            </div>
          </div>

          <button onclick="openCompatibilityModal()" class="w-full py-3 bg-gradient-to-r from-rose-500 to-orange-500 text-white font-black rounded-2xl shadow-sm text-xs flex items-center justify-center gap-1.5">
            <i data-lucide="sparkles" class="w-4 h-4"></i>
            <span>우리 초코와 친구 궁합 측정하기</span>
          </button>
        </div>

      </section>

      <!-- ================= 4. DOCTOR CHART TAB (스마트 닥터 차트) ================= -->
      <section id="view-chart" class="tab-view hidden p-4 space-y-4">
        
        <div class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-3xl p-5 shadow-md">
          <div class="flex items-center justify-between">
            <span class="text-xs bg-white/20 px-2.5 py-0.5 rounded-full font-bold">🩺 동물병원 원장님 전송 차트</span>
            <span class="text-xs text-blue-100">원클릭 PDF / 카톡</span>
          </div>
          <h3 class="text-xl font-black mt-2">일일 V-체크 건강 일기</h3>
          <p class="text-xs text-blue-100 mt-1">오늘의 식욕, 배변, 증상을 3초 만에 기록하세요.</p>
        </div>

        <!-- Daily Quick Checklist Form -->
        <div class="pet-card rounded-3xl p-5 space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-black text-slate-800">📅 기록 일자</span>
            <input type="date" id="chart-date-input" class="text-xs p-1.5 rounded-xl border border-slate-200 font-bold bg-slate-50">
          </div>

          <!-- Appetite -->
          <div class="space-y-1.5">
            <span class="text-xs font-bold text-slate-600">🍖 식욕 상태</span>
            <div class="grid grid-cols-4 gap-1.5 text-xs">
              <button onclick="selectCheck(this, 'appetite', '매우좋음')" class="check-btn py-2 rounded-xl text-center">매우좋음</button>
              <button onclick="selectCheck(this, 'appetite', '정상')" class="check-btn active py-2 rounded-xl text-center">정상</button>
              <button onclick="selectCheck(this, 'appetite', '약간감소')" class="check-btn py-2 rounded-xl text-center">약간감소</button>
              <button onclick="selectCheck(this, 'appetite', '거의안먹음')" class="check-btn py-2 rounded-xl text-center">안먹음</button>
            </div>
          </div>

          <!-- Stool -->
          <div class="space-y-1.5">
            <span class="text-xs font-bold text-slate-600">💩 대변 상태</span>
            <div class="grid grid-cols-4 gap-1.5 text-xs">
              <button onclick="selectCheck(this, 'stool', '정상변')" class="check-btn active py-2 rounded-xl text-center">정상변</button>
              <button onclick="selectCheck(this, 'stool', '묽은변')" class="check-btn py-2 rounded-xl text-center">묽은변</button>
              <button onclick="selectCheck(this, 'stool', '설사')" class="check-btn py-2 rounded-xl text-center">설사</button>
              <button onclick="selectCheck(this, 'stool', '혈변/점액')" class="check-btn py-2 rounded-xl text-center">혈변</button>
            </div>
          </div>

          <!-- Symptoms -->
          <div class="space-y-1.5">
            <span class="text-xs font-bold text-slate-600">⚠️ 이상 징후 (다중 선택 가능)</span>
            <div class="grid grid-cols-3 gap-1.5 text-xs">
              <button onclick="toggleMultiCheck(this, '구토')" class="symptom-btn py-2 rounded-xl text-center">구토</button>
              <button onclick="toggleMultiCheck(this, '기침/켁켁')" class="symptom-btn py-2 rounded-xl text-center">기침/켁켁</button>
              <button onclick="toggleMultiCheck(this, '가려움/긁음')" class="symptom-btn py-2 rounded-xl text-center">가려움</button>
              <button onclick="toggleMultiCheck(this, '눈물/눈곱')" class="symptom-btn py-2 rounded-xl text-center">눈물/눈곱</button>
              <button onclick="toggleMultiCheck(this, '절뚝거림')" class="symptom-btn py-2 rounded-xl text-center">다리절음</button>
              <button onclick="toggleMultiCheck(this, '기력저하')" class="symptom-btn py-2 rounded-xl text-center">기력저하</button>
            </div>
          </div>

          <!-- Memo -->
          <div class="space-y-1.5">
            <span class="text-xs font-bold text-slate-600">📝 특이사항 메모</span>
            <input type="text" id="chart-memo-input" placeholder="산책 시간, 약 복용 상태 등을 기록하세요" class="w-full text-xs p-3 rounded-2xl border border-slate-200 bg-slate-50">
          </div>

          <!-- Actions -->
          <div class="pt-2 flex gap-2">
            <button onclick="saveHealthLog()" class="flex-1 py-3 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl text-xs shadow-sm">
              오늘 기록 저장하기
            </button>
            <button onclick="exportDoctorChartPDF()" class="px-4 py-3 bg-slate-900 hover:bg-black text-white font-bold rounded-2xl text-xs flex items-center gap-1.5 shadow-sm">
              <i data-lucide="download" class="w-3.5 h-3.5"></i>
              <span>PDF 출력</span>
            </button>
          </div>
        </div>

        <!-- History Records -->
        <div class="space-y-2">
          <span class="text-xs font-black text-slate-800 px-1">📋 최근 기록 내역</span>
          <div id="chart-history-list" class="space-y-2"></div>
        </div>

      </section>

      <!-- ================= 5. SETTINGS & PROFILE TAB (설정 & 계정 센터) ================= -->
      <section id="view-settings" class="tab-view hidden p-4 space-y-3">
        
        <!-- User Profile Card -->
        <div id="settings-user-box" class="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-3xl p-5 shadow-sm">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div id="user-avatar-badge" class="w-14 h-14 rounded-full bg-blue-600 text-white flex items-center justify-center text-2xl font-bold shadow-md overflow-hidden">
                🐶
              </div>
              <div>
                <div class="flex items-center gap-1.5">
                  <span id="user-display-name" class="font-black text-base text-slate-900">게스트 보호자님</span>
                  <span id="user-provider-badge" class="text-[10px] px-2 py-0.5 rounded-full bg-slate-200 text-slate-700 font-bold">비회원</span>
                </div>
                <p id="user-email-text" class="text-xs text-slate-500 mt-0.5">로그인하고 차트 클라우드 동기화</p>
              </div>
            </div>
            <button id="btn-settings-auth" onclick="openAuthModal()" class="px-3.5 py-2 rounded-2xl bg-blue-600 text-white text-xs font-black shadow-sm hover:bg-blue-700">
              로그인
            </button>
          </div>
        </div>

        <!-- Menu Links -->
        <div class="pet-card rounded-3xl p-2 divide-y divide-slate-100 text-sm">
          <button onclick="switchTab('compat')" class="w-full flex items-center justify-between p-3.5 hover:bg-slate-50 rounded-2xl transition-colors">
            <div class="flex items-center gap-3">
              <span class="text-lg">💌</span>
              <span class="font-bold text-slate-800">친구 초대 & 멍냥 궁합 공유</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
          </button>

          <button onclick="openMapModal()" class="w-full flex items-center justify-between p-3.5 hover:bg-slate-50 rounded-2xl transition-colors">
            <div class="flex items-center gap-3">
              <span class="text-lg">🗺️</span>
              <span class="font-bold text-slate-800">카카오 공식 1km 펫지도</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
          </button>

          <button onclick="alert('📢 v2.6.0 최신 버전입니다. (모든 핵심 기능 정상 작동)')" class="w-full flex items-center justify-between p-3.5 hover:bg-slate-50 rounded-2xl transition-colors">
            <div class="flex items-center gap-3">
              <span class="text-lg">✨</span>
              <span class="font-bold text-slate-800">앱 버전 정보 (v2.6.0 최신판)</span>
            </div>
            <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
          </button>
        </div>

      </section>

    </main>

    <!-- Bottom Navigation Bar (Wayo Style Bright White Bar + Safe Area) -->
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

    </nav>

    <!-- ================= MODALS ================= -->

    <!-- Modal: Social Auth (Kakao & Google) -->
    <div id="modal-auth" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🐾</span>
            <h3 class="font-black text-base text-slate-900">간편 소셜 로그인</h3>
          </div>
          <button onclick="closeAuthModal()" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>

        <div class="text-center py-2">
          <div class="w-16 h-16 rounded-full bg-blue-50 mx-auto flex items-center justify-center text-3xl mb-2 shadow-inner">
            🐶
          </div>
          <h4 class="font-black text-sm text-slate-900">펫로그 AI 시작하기</h4>
          <p class="text-xs text-slate-500 mt-1">소셜 계정으로 1초 만에 가입하고<br>우리 아이 건강 기록을 안전하게 보관하세요.</p>
        </div>

        <!-- Social Buttons -->
        <div class="space-y-2">
          <button onclick="loginWithKakao()" class="w-full py-3 px-4 rounded-2xl bg-[#FEE500] hover:bg-[#FDD835] text-[#191919] font-black text-xs flex items-center justify-center gap-2.5 shadow-sm transition-transform active:scale-98">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3C6.477 3 2 6.477 2 10.8c0 2.8 1.88 5.25 4.7 6.6l-.96 3.53c-.08.31.25.56.51.38l4.24-2.82c.49.07.99.11 1.51.11 5.523 0 10-3.477 10-7.8S17.523 3 12 3z"/>
            </svg>
            <span>카카오로 1초 시작하기</span>
          </button>

          <button onclick="loginWithGoogle()" class="w-full py-3 px-4 rounded-2xl bg-white hover:bg-slate-50 text-slate-800 font-bold text-xs flex items-center justify-center gap-2.5 border border-slate-300 shadow-sm transition-transform active:scale-98">
            <svg class="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span>Google 계정으로 계속하기</span>
          </button>
        </div>

        <div class="pt-2 text-center border-t border-slate-100">
          <button onclick="closeAuthModal()" class="text-[11px] text-slate-400 hover:text-slate-600 underline">
            로그인 없이 둘러보기
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Free Trial Limit Reached -->
    <div id="modal-trial-limit" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🎁</span>
            <h3 class="font-black text-sm text-slate-900">1회 무료 체험 완료</h3>
          </div>
          <button onclick="closeTrialLimitModal()" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <div class="text-center py-2">
          <div class="w-16 h-16 rounded-full bg-blue-50 mx-auto flex items-center justify-center text-3xl mb-2 shadow-inner">
            🔒
          </div>
          <h4 id="limit-feature-name" class="font-black text-sm text-slate-900">비회원 무료 체험 1회를 모두 사용하셨습니다</h4>
          <p class="text-xs text-slate-500 mt-1.5">
            <strong>카카오 / 구글 1초 회원가입</strong>만 하시면<br>
            AI 사진 진단, 멍냥 궁합, 닥터 차트 등<br>
            <span class="text-blue-600 font-black">모든 핵심 기능을 평생 무제한 무료</span>로 이용하실 수 있습니다!
          </p>
        </div>

        <!-- Social Buttons -->
        <div class="space-y-2 pt-1">
          <button onclick="closeTrialLimitModal(); loginWithKakao();" class="w-full py-3 px-4 rounded-2xl bg-[#FEE500] text-[#191919] font-black text-xs flex items-center justify-center gap-2 shadow-sm">
            <span>카카오로 1초 가입하고 무제한 무료 이용</span>
          </button>
          <button onclick="closeTrialLimitModal(); loginWithGoogle();" class="w-full py-3 px-4 rounded-2xl bg-white border border-slate-300 text-slate-800 font-bold text-xs flex items-center justify-center gap-2 shadow-sm">
            <span>Google 계정으로 무제한 무료 이용</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: PRO Paid Feature -->
    <div id="modal-pro-service" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl">
        <div class="flex justify-between items-center border-b border-slate-100 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-2xl">👑</span>
            <h3 class="font-black text-sm text-amber-600">펫로그 PRO 유료 서비스</h3>
          </div>
          <button onclick="closeProServiceModal()" class="p-1.5 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <div class="space-y-2">
          <h4 id="pro-modal-title" class="font-black text-base text-slate-900">24시 수의사 1:1 상담</h4>
          <p id="pro-modal-desc" class="text-xs text-slate-500">전문 수의사의 임상 진단 소견서 및 약물 복용 가이드 제공</p>
          <div class="p-3 bg-amber-50 rounded-2xl border border-amber-200 flex items-center justify-between">
            <span class="text-xs text-amber-900 font-bold">이용 요금</span>
            <span id="pro-modal-price" class="text-sm font-black text-amber-600">29,000원</span>
          </div>
        </div>

        <button onclick="requestProServiceOrder()" class="w-full py-3 rounded-2xl bg-gradient-to-r from-amber-500 to-orange-500 text-white font-black text-xs shadow-md hover:opacity-95 transition-all">
          전문가 1:1 매칭 신청하기
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

        <div class="relative h-64 bg-slate-100 overflow-hidden shrink-0 border-b border-slate-200">
          <div id="kakao-map-container" class="w-full h-full"></div>
          <button onclick="getUserGPSLocation()" class="absolute bottom-3 right-3 bg-white text-slate-800 p-2.5 rounded-full shadow-xl border border-slate-200 z-10" title="내 위치">
            <i data-lucide="crosshair" class="w-4 h-4 text-blue-600"></i>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-2.5" id="map-places-container"></div>
      </div>
    </div>

    <!-- Modal: Compatibility & MBTI -->
    <div id="modal-compatibility" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl">
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
          <span class="text-xs font-black text-rose-600">💖 AI 멍냥 케미 분석</span>
          <button onclick="closeCompatibilityModal()" class="p-1 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <div class="space-y-3">
          <div class="flex items-center justify-center gap-3 py-2">
            <div class="text-center">
              <div class="w-14 h-14 rounded-full bg-blue-50 flex items-center justify-center text-3xl border-2 border-blue-400 shadow-sm">🐕</div>
              <span class="text-xs font-bold mt-1 block">우리 초코</span>
            </div>
            <div class="text-2xl font-black text-rose-500 animate-bounce">❤️</div>
            <div class="text-center">
              <select id="compat-partner-select" onchange="calcCompatibility()" class="w-24 text-xs p-1.5 rounded-xl bg-slate-50 border border-slate-200 font-bold">
                <option value="poodle">토이푸들 뽀삐</option>
                <option value="retriever">리트리버 몽이</option>
                <option value="cat_luna">고양이 루나</option>
                <option value="corgi">웰시코기 둥이</option>
              </select>
              <span class="text-xs font-bold mt-1 block">친구 아이</span>
            </div>
          </div>

          <div id="compat-result-box" class="p-4 bg-rose-50 rounded-2xl border border-rose-100 text-center space-y-1.5">
            <div class="text-2xl font-black text-rose-600">케미 지수 95% 💕</div>
            <p class="text-xs font-bold text-slate-800">"환상의 산책 메이트! 서로의 에너지를 채워줘요."</p>
            <p class="text-[11px] text-slate-500">놀이 궁합: ⭐⭐⭐⭐⭐ | 소통 케미: ⭐⭐⭐⭐</p>
          </div>

          <button onclick="shareCompatResult()" class="w-full py-3 bg-[#FEE500] hover:bg-[#FDD835] text-[#191919] font-black rounded-2xl text-xs flex items-center justify-center gap-2 shadow-sm">
            <span>카카오톡으로 이 궁합 결과 공유하기 💬</span>
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
    f.write(bright_html)

print("index.html rebuilt with bright Wayo-style design.")
