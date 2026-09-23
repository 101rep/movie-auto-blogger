import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"
app_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\app.js"

with open(index_file, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Header to add Mode Switch (Owner vs Sitter)
old_header_branding = """        <div class="flex items-center gap-1.5">
          <span class="text-2xl animate-gentle">🐾</span>
          <h1 id="header-title" class="text-2xl font-black tracking-tight text-blue-600">petlog</h1>
        </div>"""

new_header_branding = """        <div class="flex items-center gap-2">
          <span class="text-2xl animate-gentle">🐾</span>
          <h1 id="header-title" class="text-xl font-black tracking-tight theme-target-color">petlog</h1>
          <!-- Dual Mode Switcher Pill -->
          <div class="flex bg-slate-100 p-0.5 rounded-full text-[10px] font-bold border border-slate-200 ml-1">
            <button id="btn-mode-owner" onclick="switchAppMode('owner')" class="px-2 py-0.5 rounded-full bg-white text-blue-600 shadow-sm font-black transition-all">🐕 견주</button>
            <button id="btn-mode-sitter" onclick="switchAppMode('sitter')" class="px-2 py-0.5 rounded-full text-slate-500 hover:text-slate-800 transition-all">🏠 펫시터</button>
          </div>
        </div>"""

html = html.replace(old_header_branding, new_header_branding)

# 2. Add Petsitter Section, Live GPS Stories, Neighborhood Exchange to Home View
sitter_and_ecosystem_html = """
        <!-- 🎥 [SHORTFORM MOMENTS] 10초 실시간 멍스토리 릴스 바 -->
        <div class="pet-card rounded-3xl p-3.5 bg-gradient-to-r from-orange-50/60 via-pink-50/40 to-purple-50/60 border border-orange-100 shadow-sm">
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
                  <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-2xl shadow-inner">🐕</div>
                </div>
              </div>
              <span class="text-[10px] font-bold text-slate-700">초코 (지금 놀이중)</span>
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

        <!-- 🏡 [WAYO STYLE] 우리 동네 가정집 펫시터 탐색 & AI 사전 성향 궁합 -->
        <div class="space-y-3 pt-1">
          <div class="flex items-center justify-between px-1">
            <div>
              <h3 class="text-base font-black text-slate-900">🏡 우리 동네 안심 펫시터</h3>
              <p class="text-[11px] text-slate-400">가정집 밀착 케어 • 전문 훈련사 • 단독 케어</p>
            </div>
            <button onclick="openSitterFilterModal()" class="flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 text-xs font-bold border border-slate-200">
              <i data-lucide="sliders-horizontal" class="w-3 h-3"></i>
              <span>거리순</span>
            </button>
          </div>

          <!-- Sitter Card 1: 김은지 펫시터 -->
          <div class="pet-card rounded-3xl overflow-hidden border border-slate-100 shadow-sm hover:border-blue-300 transition-all">
            <!-- House Photo Header -->
            <div class="relative h-44 bg-slate-200 overflow-hidden cursor-pointer" onclick="openSitterDetailModal(1)">
              <img src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&auto=format&fit=crop&q=80" alt="가정집 거실" class="w-full h-full object-cover">
              <div class="absolute top-3 left-3 flex gap-1.5">
                <span class="bg-blue-600 text-white font-black text-[10px] px-2.5 py-0.5 rounded-full shadow">단독 케어</span>
                <span class="bg-emerald-600 text-white font-black text-[10px] px-2.5 py-0.5 rounded-full shadow">24시 상주</span>
              </div>
              <div class="absolute bottom-2 right-3 bg-black/60 backdrop-blur-md text-white px-2 py-0.5 rounded-full text-[10px] font-bold">
                📸 거실 5장 보기
              </div>
            </div>

            <!-- Content -->
            <div class="p-4 space-y-2.5">
              <div class="flex items-center justify-between">
                <div>
                  <div class="flex items-center gap-1.5">
                    <h4 class="font-black text-sm text-slate-900">김은지 펫시터</h4>
                    <span class="text-xs font-bold text-amber-500 flex items-center">⭐ 4.98 <span class="text-[10px] text-slate-400 ml-0.5">(후기 42)</span></span>
                  </div>
                  <p class="text-[11px] text-slate-500 mt-0.5">서울 강남구 역삼동 • 도보 350m</p>
                </div>
                <div class="text-right">
                  <span class="text-[10px] text-slate-400">1박 돌봄</span>
                  <p class="text-base font-black text-slate-900">71,600원</p>
                </div>
              </div>

              <!-- AI 사전 성향 궁합 뱃지 -->
              <div class="p-2.5 bg-blue-50/80 rounded-2xl border border-blue-100 flex items-center justify-between">
                <div class="flex items-center gap-1.5">
                  <span class="text-sm">✨</span>
                  <div>
                    <span class="text-[11px] font-black text-blue-700">우리 초코와의 AI 안심 궁합 99%</span>
                    <p class="text-[9px] text-slate-500">낯가림 적음 • 실내 패드 배변 환경 완벽 일치</p>
                  </div>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-blue-600 text-white font-bold shrink-0">찰떡매칭</span>
              </div>

              <div class="flex gap-2 pt-1">
                <button onclick="openLiveWalkGpsModal('초코', '김은지 펫시터')" class="flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-2xl text-xs flex items-center justify-center gap-1">
                  <i data-lucide="navigation" class="w-3.5 h-3.5 text-blue-600"></i>
                  <span>산책 LIVE GPS</span>
                </button>
                <button onclick="openSitterDetailModal(1)" class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl text-xs shadow-sm">
                  1:1 돌봄 예약 신청
                </button>
              </div>
            </div>
          </div>

          <!-- Sitter Card 2: 박서준 훈련사 펫시터 -->
          <div class="pet-card rounded-3xl overflow-hidden border border-slate-100 shadow-sm hover:border-blue-300 transition-all">
            <!-- House Photo Header -->
            <div class="relative h-44 bg-slate-200 overflow-hidden cursor-pointer" onclick="openSitterDetailModal(2)">
              <img src="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=600&auto=format&fit=crop&q=80" alt="가정집 거실" class="w-full h-full object-cover">
              <div class="absolute top-3 left-3 flex gap-1.5">
                <span class="bg-rose-600 text-white font-black text-[10px] px-2.5 py-0.5 rounded-full shadow">전문 훈련사</span>
                <span class="bg-amber-600 text-white font-black text-[10px] px-2.5 py-0.5 rounded-full shadow">마당 보유</span>
              </div>
            </div>

            <!-- Content -->
            <div class="p-4 space-y-2.5">
              <div class="flex items-center justify-between">
                <div>
                  <div class="flex items-center gap-1.5">
                    <h4 class="font-black text-sm text-slate-900">박서준 전문훈련사</h4>
                    <span class="text-xs font-bold text-amber-500 flex items-center">⭐ 5.0 <span class="text-[10px] text-slate-400 ml-0.5">(후기 68)</span></span>
                  </div>
                  <p class="text-[11px] text-slate-500 mt-0.5">서울 강남구 역삼동 • 720m</p>
                </div>
                <div class="text-right">
                  <span class="text-[10px] text-slate-400">1박 돌봄</span>
                  <p class="text-base font-black text-slate-900">88,000원</p>
                </div>
              </div>

              <!-- AI 사전 성향 궁합 뱃지 -->
              <div class="p-2.5 bg-orange-50/80 rounded-2xl border border-orange-100 flex items-center justify-between">
                <div class="flex items-center gap-1.5">
                  <span class="text-sm">🎓</span>
                  <div>
                    <span class="text-[11px] font-black text-orange-700">우리 초코와의 AI 안심 궁합 95%</span>
                    <p class="text-[9px] text-slate-500">분리불안 케어 전문 • 천연 잔디 마당 산책</p>
                  </div>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-orange-500 text-white font-bold shrink-0">안심코칭</span>
              </div>

              <div class="flex gap-2 pt-1">
                <button onclick="openLiveWalkGpsModal('초코', '박서준 훈련사')" class="flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-2xl text-xs flex items-center justify-center gap-1">
                  <i data-lucide="navigation" class="w-3.5 h-3.5 text-blue-600"></i>
                  <span>산책 LIVE GPS</span>
                </button>
                <button onclick="openSitterDetailModal(2)" class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl text-xs shadow-sm">
                  1:1 돌봄 예약 신청
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 🛡️ [AIRCOVER] 펫로그 안심 케어 최대 500만원 보상 보증제 배너 -->
        <div class="bg-gradient-to-r from-emerald-500/15 via-teal-500/10 to-blue-500/15 border border-emerald-500/30 rounded-3xl p-4 flex items-center justify-between shadow-sm">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-2xl bg-emerald-500 text-white flex items-center justify-center text-xl shadow">
              🛡️
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <span class="text-xs font-black text-emerald-800">펫로그 안심 100% 보증제</span>
                <span class="text-[9px] bg-emerald-600 text-white font-black px-1.5 py-0.2 rounded-full">에어커버</span>
              </div>
              <p class="text-[11px] text-slate-600 mt-0.5">돌봄 중 사고/질병 발생 시 최대 500만원 병원비 무상 지원</p>
            </div>
          </div>
        </div>

        <!-- 🏘️ [COMMUNITY] 동네 멍친구 무료 품앗이 돌봄 & 산책 번개 코너 -->
        <div class="pet-card rounded-3xl p-4 border border-slate-100 shadow-sm space-y-3">
          <div class="flex items-center justify-between px-1">
            <div class="flex items-center gap-1.5">
              <span class="text-base">🏘️</span>
              <div>
                <h4 class="font-black text-xs text-slate-900">동네 멍친구 무료 돌봄 품앗이 & 산책 번개</h4>
                <p class="text-[10px] text-slate-400">역삼1동 이웃 견주끼리 상호 무료 돌봄</p>
              </div>
            </div>
            <button onclick="openCommunityExchangeModal()" class="text-xs font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full">
              + 글쓰기
            </button>
          </div>

          <div class="space-y-2">
            <div onclick="openCommunityExchangeDetail('역삼 래미안 102동 뽀삐맘', '오늘 오후 2시~4시 산책 같이해요 🐾')" class="p-3 bg-slate-50 rounded-2xl border border-slate-100 flex items-center justify-between cursor-pointer hover:border-blue-300">
              <div class="flex items-center gap-2.5">
                <span class="text-xl">🐩</span>
                <div>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[11px] font-bold text-slate-800">오늘 오후 2시~4시 산책 같이해요</span>
                    <span class="text-[9px] bg-blue-100 text-blue-700 px-1.5 py-0.2 rounded font-bold">산책번개</span>
                  </div>
                  <p class="text-[10px] text-slate-400 mt-0.5">역삼 래미안 뽀삐맘 • 150m</p>
                </div>
              </div>
              <span class="text-xs text-blue-600 font-bold">참여 3명</span>
            </div>

            <div onclick="openCommunityExchangeDetail('역삼 센트럴 루나아빠', '내일 급한 병원 일정 동안 2시간 무료 품앗이 돌봄 구해요!')" class="p-3 bg-slate-50 rounded-2xl border border-slate-100 flex items-center justify-between cursor-pointer hover:border-blue-300">
              <div class="flex items-center gap-2.5">
                <span class="text-xl">🐕</span>
                <div>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[11px] font-bold text-slate-800">내일 2시간 무료 품앗이 돌봄</span>
                    <span class="text-[9px] bg-amber-100 text-amber-800 px-1.5 py-0.2 rounded font-bold">돌봄품앗이</span>
                  </div>
                  <p class="text-[10px] text-slate-400 mt-0.5">역삼 센트럴 루나아빠 • 400m</p>
                </div>
              </div>
              <span class="text-xs text-amber-600 font-bold">매칭중</span>
            </div>
          </div>
        </div>

        <!-- 💰 [RECRUIT] 펫시터 지원하기 배너 -->
        <div onclick="openSitterRegisterModal()" class="bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-3xl p-4 shadow-md flex items-center justify-between cursor-pointer hover:opacity-95 transition-all">
          <div>
            <span class="text-[10px] bg-black/30 px-2 py-0.5 rounded-full font-bold">펫시터 파트너 모집</span>
            <h4 class="font-black text-sm text-white mt-1">집에서 강아지 돌보며 월 150만원 수익! 🏠</h4>
            <p class="text-[11px] text-amber-100">원하는 날짜만 자유롭게 예약 받는 펫로그 펫시터 지원하기</p>
          </div>
          <span class="text-2xl">👉</span>
        </div>
"""

# Insert into view-home before 3-column quick services
if '<!-- 🎥 [SHORTFORM MOMENTS]' not in html:
    html = html.replace('<!-- 3-Column Quick Services Icons', sitter_and_ecosystem_html + '\n\n        <!-- 3-Column Quick Services Icons')

# 3. Add Sitter Dashboard View (view-sitter-dashboard)
sitter_dashboard_view_html = """
      <!-- ================= 6. SITTER DASHBOARD TAB (펫시터 파트너 센터) ================= -->
      <section id="view-sitter-dashboard" class="tab-view hidden p-4 space-y-4">
        
        <!-- Sitter Revenue Card -->
        <div class="bg-gradient-to-r from-slate-900 to-indigo-950 text-white rounded-3xl p-5 shadow-lg relative overflow-hidden">
          <div class="flex items-center justify-between">
            <span class="text-xs bg-amber-400 text-slate-950 font-black px-2.5 py-0.5 rounded-full">
              🏠 펫시터 파트너 센터
            </span>
            <span class="text-xs text-slate-400">9월 정산 완료</span>
          </div>
          <div class="mt-3">
            <span class="text-xs text-slate-300">이번 달 누적 돌봄 수익</span>
            <div class="flex items-baseline gap-1.5 mt-0.5">
              <h3 class="text-3xl font-black text-amber-400">1,450,000</h3>
              <span class="text-sm font-bold text-white">원</span>
            </div>
          </div>
          <div class="grid grid-cols-3 gap-2 pt-3 border-t border-slate-800 mt-3 text-center">
            <div>
              <span class="text-[10px] text-slate-400 block">돌봄 완료</span>
              <span class="text-xs font-black text-white">21회</span>
            </div>
            <div>
              <span class="text-[10px] text-slate-400 block">고객 만족도</span>
              <span class="text-xs font-black text-amber-400">⭐ 4.98</span>
            </div>
            <div>
              <span class="text-[10px] text-slate-400 block">단골 견주</span>
              <span class="text-xs font-black text-emerald-400">14명</span>
            </div>
          </div>
        </div>

        <!-- New Booking Requests Inbox -->
        <div class="pet-card rounded-3xl p-5 space-y-3">
          <div class="flex items-center justify-between">
            <h4 class="font-black text-sm text-slate-900">📩 신규 돌봄 예약 신청 (1건)</h4>
            <span class="text-xs text-rose-500 font-bold animate-pulse">응답 대기중</span>
          </div>

          <div class="p-3.5 bg-blue-50/60 rounded-2xl border border-blue-100 space-y-2">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <span class="text-2xl">🐕</span>
                <div>
                  <h5 class="font-black text-xs text-slate-900">초코 (말티즈 • 3세 • 3.4kg)</h5>
                  <p class="text-[10px] text-slate-500">10월 2일 ~ 10월 3일 (1박 위탁돌봄)</p>
                </div>
              </div>
              <span class="text-xs font-black text-blue-600">71,600원</span>
            </div>
            <p class="text-[11px] text-slate-600 bg-white p-2 rounded-xl border border-slate-100">
              "사료 아침/저녁 1회씩 급여 부탁드립니다. 낯가림이 조금 있으나 장난감 놀이를 좋아해요!"
            </p>
            <div class="flex gap-2 pt-1">
              <button onclick="acceptBookingRequest('초코')" class="flex-1 py-2 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-xl text-xs shadow-sm">
                예약 승인하기
              </button>
              <button onclick="rejectBookingRequest('초코')" class="px-3 py-2 bg-slate-200 text-slate-700 font-bold rounded-xl text-xs">
                거절
              </button>
            </div>
          </div>
        </div>

        <!-- Live Care Action Tools for Sitter -->
        <div class="pet-card rounded-3xl p-5 space-y-3">
          <h4 class="font-black text-sm text-slate-900">🐾 실시간 LIVE 돌봄 관제 도구</h4>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <button onclick="openLiveWalkGpsModal('초코', '김은지 펫시터')" class="p-3 bg-slate-50 hover:bg-blue-50 rounded-2xl border border-slate-200 flex flex-col items-center gap-1.5 text-center">
              <span class="text-2xl">📍</span>
              <span class="font-black text-slate-800">산책 LIVE GPS 시작</span>
              <span class="text-[10px] text-blue-600">경로 & 💩 배변 기록</span>
            </button>
            <button onclick="openShortStoryModal('초코', '김은지 펫시터', '신나는 터그놀이 타임 🧸', '🐕')" class="p-3 bg-slate-50 hover:bg-pink-50 rounded-2xl border border-slate-200 flex flex-col items-center gap-1.5 text-center">
              <span class="text-2xl">🎥</span>
              <span class="font-black text-slate-800">10초 멍스토리 전송</span>
              <span class="text-[10px] text-pink-600">견주 인스타 릴스 연동</span>
            </button>
          </div>
          <button onclick="syncSitterLogToDoctorChart('초코')" class="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-black rounded-2xl text-xs flex items-center justify-center gap-1.5 shadow-sm">
            <i data-lucide="check-circle" class="w-4 h-4"></i>
            <span>오늘 돌봄 일지 $\rightarrow$ 견주 [스마트 닥터 차트]에 1초 자동 전송</span>
          </button>
        </div>

      </section>
"""

if 'id="view-sitter-dashboard"' not in html:
    html = html.replace('<!-- ================= 5. SETTINGS & PROFILE TAB', sitter_dashboard_view_html + '\n\n      <!-- ================= 5. SETTINGS & PROFILE TAB')

# 4. Add Full Sitter Modals (Detail, Register, Live GPS Walk, Short Story, Community Exchange)
full_sitter_modals_html = """
    <!-- ================= Modal: Sitter Detail Profile & Booking ================= -->
    <div id="modal-sitter-detail" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-md bg-white h-full sm:h-[90vh] sm:rounded-3xl flex flex-col border border-slate-200 animate-slide-up overflow-hidden text-left shadow-2xl">
        <!-- Header Image Carousel -->
        <div class="relative h-56 bg-slate-200 shrink-0">
          <img id="sitter-modal-img" src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&auto=format&fit=crop&q=80" class="w-full h-full object-cover">
          <button onclick="closeSitterDetailModal()" class="absolute top-3 right-3 p-2 rounded-full bg-black/50 text-white hover:bg-black/70">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
          <div class="absolute bottom-3 left-3 flex gap-1.5">
            <span id="sitter-modal-badge" class="bg-blue-600 text-white font-black text-xs px-2.5 py-0.5 rounded-full shadow">단독 케어</span>
            <span class="bg-emerald-600 text-white font-black text-xs px-2.5 py-0.5 rounded-full shadow">🛡️ 안심 500만원 보증</span>
          </div>
        </div>

        <!-- Body -->
        <div class="flex-1 overflow-y-auto p-5 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 id="sitter-modal-name" class="font-black text-lg text-slate-900">김은지 펫시터</h3>
              <p id="sitter-modal-addr" class="text-xs text-slate-500">서울 강남구 역삼동 • 도보 350m</p>
            </div>
            <div class="text-right">
              <span class="text-xs text-slate-400">1박 요금</span>
              <p id="sitter-modal-price" class="text-lg font-black text-blue-600">71,600원</p>
            </div>
          </div>

          <!-- Environment Features -->
          <div class="grid grid-cols-3 gap-2 text-center text-xs">
            <div class="p-2.5 bg-slate-50 rounded-2xl border border-slate-100">
              <span class="text-lg block mb-0.5">🛋️</span>
              <span class="font-bold text-slate-700">미끄럼방지 매트</span>
            </div>
            <div class="p-2.5 bg-slate-50 rounded-2xl border border-slate-100">
              <span class="text-lg block mb-0.5">🚪</span>
              <span class="font-bold text-slate-700">현관 안전문 완비</span>
            </div>
            <div class="p-2.5 bg-slate-50 rounded-2xl border border-slate-100">
              <span class="text-lg block mb-0.5">💊</span>
              <span class="font-bold text-slate-700">투약/노령견 케어</span>
            </div>
          </div>

          <!-- AI Matching Reason -->
          <div class="p-3.5 bg-blue-50 rounded-2xl border border-blue-100 space-y-1">
            <span class="text-xs font-black text-blue-700 flex items-center gap-1">
              <span>✨ AI 안심 궁합 리포트</span>
              <span class="text-[10px] bg-blue-600 text-white px-1.5 rounded">99점</span>
            </span>
            <p class="text-[11px] text-slate-600">
              초코는 낯가림이 살짝 있지만, 김은지 펫시터님의 조용한 단독 케어 환경과 실내 놀이 코칭에 가장 빠르게 적응할 것으로 분석되었습니다.
            </p>
          </div>

          <!-- Booking Actions -->
          <div class="pt-2 flex gap-2">
            <button onclick="startSitterChat()" class="px-4 py-3 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold rounded-2xl text-xs flex items-center gap-1">
              <i data-lucide="message-circle" class="w-4 h-4 text-blue-600"></i>
              <span>1:1 사전 채팅</span>
            </button>
            <button onclick="requestSitterBooking()" class="flex-1 py-3 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl text-xs shadow-md">
              이 펫시터에게 돌봄 예약 신청하기
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= Modal: Live Walking GPS & Stamp Tracker ================= -->
    <div id="modal-live-walk-gps" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-md bg-white h-full sm:h-[90vh] sm:rounded-3xl flex flex-col border border-slate-200 animate-slide-up overflow-hidden text-left shadow-2xl">
        <div class="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between shrink-0 bg-white">
          <div class="flex items-center gap-2">
            <div class="gps-pulse-marker"></div>
            <div>
              <h3 class="font-black text-sm text-slate-900">실시간 산책 LIVE GPS 관제</h3>
              <p id="walk-live-title" class="text-[10px] text-slate-400">초코 & 김은지 펫시터 (산책 24분째)</p>
            </div>
          </div>
          <button onclick="closeLiveWalkGpsModal()" class="p-1 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>

        <!-- GPS Simulated Map Box -->
        <div class="relative h-64 bg-slate-100 overflow-hidden shrink-0 border-b border-slate-200">
          <div id="live-walk-map-container" class="w-full h-full"></div>
          <div class="absolute top-3 left-3 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-full shadow border text-[11px] font-black text-blue-600 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-blue-600 animate-ping"></span>
            <span>산책 거리 1.2km • 2,450보</span>
          </div>
        </div>

        <!-- Real-time Event Stamps List -->
        <div class="flex-1 overflow-y-auto p-4 space-y-2">
          <span class="text-xs font-black text-slate-800 block px-1">📍 산책 중 실시간 스탬프 기록</span>
          
          <div class="p-3 bg-amber-50/80 rounded-2xl border border-amber-200 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <span class="text-2xl">💩</span>
              <div>
                <span class="text-xs font-black text-amber-900">14:20 황금변 완료 (사진 인증)</span>
                <p class="text-[10px] text-slate-500">역삼공원 벤치 옆 잔디밭 • 정상 굳기</p>
              </div>
            </div>
            <span class="text-[10px] bg-amber-500 text-white font-bold px-2 py-0.5 rounded-full">인증완료</span>
          </div>

          <div class="p-3 bg-blue-50/80 rounded-2xl border border-blue-200 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <span class="text-2xl">💧</span>
              <div>
                <span class="text-xs font-black text-blue-900">14:28 깨끗한 생수 80ml 음수 완료</span>
                <p class="text-[10px] text-slate-500">휴대용 보틀로 시원하게 마셨습니다</p>
              </div>
            </div>
            <span class="text-[10px] bg-blue-600 text-white font-bold px-2 py-0.5 rounded-full">수분보충</span>
          </div>

          <div class="p-3 bg-rose-50/80 rounded-2xl border border-rose-200 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <span class="text-2xl">⚡</span>
              <div>
                <span class="text-xs font-black text-rose-900">14:35 영역 표시(소변 2회) 완료</span>
                <p class="text-[10px] text-slate-500">가로수길 냄새 맡으며 기분 좋게 걷는 중</p>
              </div>
            </div>
            <span class="text-[10px] bg-rose-500 text-white font-bold px-2 py-0.5 rounded-full">스트레스 해소</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= Modal: 10초 숏폼 멍스토리 뷰어 ================= -->
    <div id="modal-short-story" class="fixed inset-0 bg-black/90 backdrop-blur-md z-50 hidden flex items-center justify-center p-0 sm:p-4">
      <div class="w-full max-w-sm h-full sm:h-[85vh] bg-slate-950 sm:rounded-3xl flex flex-col relative overflow-hidden text-white shadow-2xl">
        <!-- Story Progress Bar -->
        <div class="absolute top-3 left-3 right-3 z-30 flex gap-1">
          <div class="flex-1 h-1 bg-white/40 rounded-full overflow-hidden">
            <div class="h-full bg-white w-full animate-pulse"></div>
          </div>
        </div>

        <!-- Story Header -->
        <div class="absolute top-6 left-4 right-4 z-30 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center text-lg font-bold" id="story-avatar">🐕</div>
            <div>
              <h4 id="story-pet-name" class="font-black text-xs text-white">초코의 오늘의 모먼트</h4>
              <p id="story-sitter-name" class="text-[10px] text-white/70">김은지 펫시터 • 방금 전</p>
            </div>
          </div>
          <button onclick="closeShortStoryModal()" class="p-1 rounded-full bg-black/40 text-white">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>

        <!-- Story Video/Image Simulator -->
        <div class="flex-1 flex flex-col items-center justify-center relative p-6 text-center">
          <div class="text-7xl mb-4 animate-bounce" id="story-emoji-large">🧸</div>
          <h3 id="story-caption" class="text-lg font-black text-white">"장난감 터그놀이 삼매경 💕"</h3>
          <p class="text-xs text-white/80 mt-1">펫시터님 댁에서 완벽 적응하고 신나게 노는 중입니다!</p>
        </div>

        <!-- Share Actions -->
        <div class="p-5 z-30 space-y-2 bg-gradient-to-t from-black via-black/80 to-transparent">
          <button onclick="shareStoryToInstagram()" class="w-full py-3 bg-gradient-to-r from-purple-600 via-pink-600 to-orange-500 text-white font-black rounded-2xl text-xs flex items-center justify-center gap-2 shadow-lg">
            <span>📷 인스타그램 스토리에 이 모먼트 공유하기</span>
          </button>
          <button onclick="shareStoryToKakao()" class="w-full py-2.5 bg-[#FEE500] text-black font-bold rounded-2xl text-xs flex items-center justify-center gap-1.5">
            <span>카카오톡으로 가족에게 보내기 💬</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ================= Modal: Sitter Registration Form ================= -->
    <div id="modal-sitter-register" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl overflow-y-auto max-h-[90vh]">
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🏠</span>
            <h3 class="font-black text-base text-slate-900">펫시터 파트너 등록 신청</h3>
          </div>
          <button onclick="closeSitterRegisterModal()" class="p-1 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>

        <div class="p-3 bg-amber-50 rounded-2xl border border-amber-200 text-xs text-amber-900">
          💰 <strong>월 평균 150만원 부수입</strong>! 우리 집 안전 환경을 등록하고 동네 이웃의 사랑스러운 아이들을 돌봐주세요.
        </div>

        <div class="space-y-3 text-xs">
          <div>
            <label class="font-bold text-slate-700 block mb-1">펫시터 닉네임 / 성함</label>
            <input type="text" id="reg-sitter-name" placeholder="예: 역삼동 다정 펫시터" class="w-full p-2.5 rounded-xl border bg-slate-50">
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">활동 거주 지역 (동/구)</label>
            <input type="text" id="reg-sitter-addr" placeholder="예: 서울 강남구 역삼동" class="w-full p-2.5 rounded-xl border bg-slate-50">
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">1박 돌봄 희망 요금 (원)</label>
            <input type="text" id="reg-sitter-price" placeholder="예: 70000" class="w-full p-2.5 rounded-xl border bg-slate-50 font-bold">
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">제공 가능 환경 / 자격증</label>
            <div class="grid grid-cols-2 gap-1.5 text-[11px] font-semibold">
              <label class="p-2 rounded-xl bg-slate-50 border flex items-center gap-1.5"><input type="checkbox" checked> 단독 케어</label>
              <label class="p-2 rounded-xl bg-slate-50 border flex items-center gap-1.5"><input type="checkbox" checked> 24시 실내 상주</label>
              <label class="p-2 rounded-xl bg-slate-50 border flex items-center gap-1.5"><input type="checkbox"> 반려견 자격증 보유</label>
              <label class="p-2 rounded-xl bg-slate-50 border flex items-center gap-1.5"><input type="checkbox"> 안전문/매트 시공</label>
            </div>
          </div>
        </div>

        <button onclick="submitSitterRegister()" class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl text-xs shadow-lg">
          펫시터 파트너 신청 완료하기 ✨
        </button>
      </div>
    </div>

    <!-- ================= Modal: Neighborhood Care Exchange ================= -->
    <div id="modal-community-exchange" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 space-y-4 border border-slate-100 animate-slide-up text-left shadow-2xl">
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🏘️</span>
            <h3 class="font-black text-base text-slate-900">동네 품앗이 돌봄 & 산책 번개</h3>
          </div>
          <button onclick="closeCommunityExchangeModal()" class="p-1 rounded-full hover:bg-slate-100 text-slate-400">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>

        <div class="space-y-3 text-xs">
          <div>
            <label class="font-bold text-slate-700 block mb-1">모집 유형</label>
            <div class="grid grid-cols-2 gap-2">
              <button type="button" class="py-2 rounded-xl bg-blue-600 text-white font-bold text-center">🐾 산책 번개</button>
              <button type="button" class="py-2 rounded-xl bg-slate-100 text-slate-700 font-bold text-center">🤝 2시간 품앗이 돌봄</button>
            </div>
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">제목 및 희망 시간</label>
            <input type="text" placeholder="예: 오늘 오후 4시 역삼공원 같이 걸어요!" class="w-full p-2.5 rounded-xl border bg-slate-50">
          </div>
        </div>

        <button onclick="alert('🎉 동네 이웃 견주들에게 산책/품앗이 알림이 등록되었습니다!'); closeCommunityExchangeModal();" class="w-full py-3 bg-blue-600 text-white font-black rounded-2xl text-xs shadow-md">
          동네 이웃에게 알림 등록하기
        </button>
      </div>
    </div>
"""

if 'id="modal-sitter-detail"' not in html:
    html = html.replace('<!-- ================= MODALS ================= -->', '<!-- ================= MODALS ================= -->\n' + full_sitter_modals_html)

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated with Full Sitter & Live GPS ecosystem.")

# 5. Update app.js with Sitter, GPS, Short Story, and Doctor Chart sync logic
with open(app_file, 'r', encoding='utf-8') as f:
    js = f.read()

sitter_app_logic = """
// ================= 11. Dual Mode & Petsitter Platform Engine =================
let currentAppMode = 'owner'; // 'owner' or 'sitter'
let liveWalkMapInstance = null;

window.switchAppMode = function(mode) {
  currentAppMode = mode;
  const btnOwner = document.getElementById('btn-mode-owner');
  const btnSitter = document.getElementById('btn-mode-sitter');
  const viewHome = document.getElementById('view-home');
  const viewSitter = document.getElementById('view-sitter-dashboard');

  if (mode === 'sitter') {
    if (btnSitter) {
      btnSitter.className = 'px-2 py-0.5 rounded-full bg-blue-600 text-white shadow-sm font-black transition-all';
    }
    if (btnOwner) {
      btnOwner.className = 'px-2 py-0.5 rounded-full text-slate-500 hover:text-slate-800 transition-all';
    }
    if (viewHome) viewHome.classList.add('hidden');
    if (viewSitter) viewSitter.classList.remove('hidden');
    alert('🏠 [펫시터 모드]로 전환되었습니다.\\n돌봄 예약 현황과 실시간 LIVE 관제 도구를 이용하실 수 있습니다.');
  } else {
    if (btnOwner) {
      btnOwner.className = 'px-2 py-0.5 rounded-full bg-white text-blue-600 shadow-sm font-black transition-all';
    }
    if (btnSitter) {
      btnSitter.className = 'px-2 py-0.5 rounded-full text-slate-500 hover:text-slate-800 transition-all';
    }
    if (viewSitter) viewSitter.classList.add('hidden');
    if (viewHome) viewHome.classList.remove('hidden');
  }

  if (window.lucide) lucide.createIcons();
};

// Sitter Profile Modal Handlers
window.openSitterDetailModal = function(id) {
  const modal = document.getElementById('modal-sitter-detail');
  if (modal) {
    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  }
};

window.closeSitterDetailModal = function() {
  const modal = document.getElementById('modal-sitter-detail');
  if (modal) modal.classList.add('hidden');
};

window.startSitterChat = function() {
  alert('💬 [1:1 안심 사전 채팅] 김은지 펫시터님과의 채팅방이 연결되었습니다.\\n아이 성향 및 픽업 여부를 자유롭게 조율하세요.');
};

window.requestSitterBooking = function() {
  if (!currentUser) {
    alert('예약 신청을 위해 먼저 간편 로그인을 진행해 주세요.');
    closeSitterDetailModal();
    openAuthModal();
    return;
  }
  alert(`🎉 [1:1 돌봄 예약 신청 완료]\\n김은지 펫시터님께 [${currentPet.name}]의 1박 위탁돌봄 신청서가 전달되었습니다.\\n승인 시 카카오 알림톡으로 안내드립니다.`);
  closeSitterDetailModal();
};

// Live Walking GPS Tracker
window.openLiveWalkGpsModal = function(petName, sitterName) {
  const modal = document.getElementById('modal-live-walk-gps');
  if (modal) {
    const title = document.getElementById('walk-live-title');
    if (title) title.textContent = `${petName} & ${sitterName} (실시간 산책 24분째)`;
    modal.classList.remove('hidden');
    setTimeout(() => {
      initLiveWalkMap();
      if (window.lucide) lucide.createIcons();
    }, 200);
  }
};

window.closeLiveWalkGpsModal = function() {
  const modal = document.getElementById('modal-live-walk-gps');
  if (modal) modal.classList.add('hidden');
};

function initLiveWalkMap() {
  const container = document.getElementById('live-walk-map-container');
  if (!container || typeof L === 'undefined') return;

  container.innerHTML = '<div id="leaflet-live-walk-map" style="width:100%; height:100%;"></div>';
  const mapEl = document.getElementById('leaflet-live-walk-map');

  if (liveWalkMapInstance) {
    try { liveWalkMapInstance.remove(); } catch(e) {}
    liveWalkMapInstance = null;
  }

  const map = L.map(mapEl, { zoomControl: false, attributionControl: false }).setView([37.498095, 127.027610], 16);
  liveWalkMapInstance = map;

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);

  // Walking Route Polyline
  const walkRoute = [
    [37.497000, 127.026000],
    [37.497500, 127.026800],
    [37.498000, 127.027200],
    [37.498095, 127.027610]
  ];

  L.polyline(walkRoute, { color: '#3b82f6', weight: 5, opacity: 0.8, dashArray: '8, 8' }).addTo(map);

  // Live Pet Marker
  const petIcon = L.divIcon({
    className: 'custom-walk-marker',
    html: '<div style="background:#3b82f6;color:white;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 0 0 6px rgba(59,130,246,0.3);border:2px solid white;">🐕</div>',
    iconSize: [34, 34],
    iconAnchor: [17, 17]
  });
  L.marker([37.498095, 127.027610], { icon: petIcon }).addTo(map).bindPopup('<b>📍 실시간 산책 위치</b><br>역삼공원 산책로 걷는 중 🐾').openPopup();

  // Poop Stamp Marker
  const poopIcon = L.divIcon({
    className: 'custom-poop-marker',
    html: '<div style="background:#ffffff;border:2px solid #f59e0b;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:15px;box-shadow:0 2px 6px rgba(0,0,0,0.2);">💩</div>',
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  });
  L.marker([37.497500, 127.026800], { icon: poopIcon }).addTo(map).bindPopup('<b>💩 황금변 1회 (14:20)</b><br>정상 굳기 확인 완료');

  setTimeout(() => { map.invalidateSize(); }, 200);
}

// 10-Second Shortform Moments Story Modal
window.openShortStoryModal = function(petName, sitterName, caption, emoji) {
  const modal = document.getElementById('modal-short-story');
  if (modal) {
    document.getElementById('story-pet-name').textContent = `${petName}의 오늘의 모먼트`;
    document.getElementById('story-sitter-name').textContent = `${sitterName} • 방금 전`;
    document.getElementById('story-caption').textContent = `"${caption}"`;
    document.getElementById('story-avatar').textContent = emoji;
    document.getElementById('story-emoji-large').textContent = emoji;
    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  }
};

window.closeShortStoryModal = function() {
  const modal = document.getElementById('modal-short-story');
  if (modal) modal.classList.add('hidden');
};

window.shareStoryToInstagram = function() {
  alert('📸 [인스타그램 스토리 공유] 인스타 스토리에 바로 올릴 수 있는 귀여운 돌봄 카드가 클립보드에 복사되었습니다!');
};

window.shareStoryToKakao = function() {
  alert('💬 [카카오톡 공유] 가족/지인에게 귀여운 10초 돌봄 모먼트 영상 링크를 발송했습니다!');
};

// Sitter Registration & Booking Management
window.openSitterRegisterModal = function() {
  const modal = document.getElementById('modal-sitter-register');
  if (modal) modal.classList.remove('hidden');
};
window.closeSitterRegisterModal = function() {
  const modal = document.getElementById('modal-sitter-register');
  if (modal) modal.classList.add('hidden');
};
window.submitSitterRegister = function() {
  const name = document.getElementById('reg-sitter-name').value.trim();
  if (!name) { alert('성함 또는 닉네임을 입력해 주세요.'); return; }
  alert(`🎉 [${name}] 펫시터 파트너 등록 신청이 접수되었습니다!\\n검증 후 24시간 이내에 펫시터 프로필이 활성화됩니다.`);
  closeSitterRegisterModal();
};

window.acceptBookingRequest = function(petName) {
  alert(`✅ [예약 승인] ${petName}의 1박 돌봄 일정이 확정되었습니다!\\n견주님께 확정 알림톡이 전송되었습니다.`);
};
window.rejectBookingRequest = function(petName) {
  alert(`예약이 취소되었습니다.`);
};

// Sync Sitter Care Log to Owner's Doctor Chart
window.syncSitterLogToDoctorChart = function(petName) {
  const newLog = {
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    appetite: '매우좋음',
    stool: '정상변',
    symptoms: [],
    medMorning: true,
    medEvening: true,
    memo: `[펫시터 전문 돌봄 일지 동기화] ${petName} 1박 위탁 돌봄 완료. 사료 2회 완식, 산책 35분(배변 1회 황금변), 수분 180ml 섭취. 특이 이상 증상 없음.`
  };
  healthLogs.unshift(newLog);
  renderChartHistory();
  alert(`🩺 [스마트 닥터 차트 동기화 완료]\\n${petName}의 오늘 돌봄 일지가 견주의 닥터 차트에 자동 병합되었습니다!`);
};

// Neighborhood Care Exchange
window.openCommunityExchangeModal = function() {
  const modal = document.getElementById('modal-community-exchange');
  if (modal) modal.classList.remove('hidden');
};
window.closeCommunityExchangeModal = function() {
  const modal = document.getElementById('modal-community-exchange');
  if (modal) modal.classList.add('hidden');
};
window.openCommunityExchangeDetail = function(user, title) {
  alert(`🏘️ [${user}]님의 동네 모임\\n"${title}"\\n\\n1:1 대화방으로 입장하여 약속을 조율하세요!`);
};
"""

if '// ================= 11. Dual Mode & Petsitter Platform' not in js:
    js = js + "\n" + sitter_app_logic

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js updated with complete Sitter & GPS & Story logic.")
