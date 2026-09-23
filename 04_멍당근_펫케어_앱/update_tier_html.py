import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"
app_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\app.js"

with open(index_file, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Free Trial / Membership Status Banner in Home View
trial_banner_html = """        <!-- Free Trial & Membership Tier Banner -->
        <div id="membership-tier-banner" onclick="openAuthModal()" class="bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-indigo-500/10 border border-amber-500/20 rounded-2xl p-3 flex items-center justify-between cursor-pointer hover:border-amber-500/40 transition-all">
          <div class="flex items-center gap-2.5">
            <span class="text-xl">🎁</span>
            <div>
              <div class="flex items-center gap-1.5">
                <span id="tier-badge-title" class="text-xs font-black text-amber-600 dark:text-amber-400">비회원 1회 무료 체험권 적용 중</span>
                <span class="text-[10px] px-1.5 py-0.2 rounded bg-amber-500 text-white font-bold">체험 모드</span>
              </div>
              <p id="tier-badge-desc" class="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5">회원가입(1초) 시 유료 기능 외 모든 핵심 기능 무제한 무료!</p>
            </div>
          </div>
          <i data-lucide="chevron-right" class="w-4 h-4 text-gray-400"></i>
        </div>"""

if 'id="membership-tier-banner"' not in html:
    html = html.replace('<!-- [PRIORITY 1] FREE AI HEALTH SCANNER', trial_banner_html + '\n\n        <!-- [PRIORITY 1] FREE AI HEALTH SCANNER')

# 2. Add PRO Paid Services Showcase section in Home or Services
pro_services_html = """        <!-- [PAID PRO SERVICES] 유료 프리미엄 멤버십 & 전문가 서비스 -->
        <div class="bg-neutral-900 text-white rounded-2xl p-4 border border-amber-500/30 shadow-lg space-y-3 relative overflow-hidden">
          <div class="absolute -right-4 -bottom-4 opacity-10 text-7xl pointer-events-none">👑</div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1.5">
              <span class="text-xs bg-amber-500 text-black font-black px-2 py-0.5 rounded-full flex items-center gap-1">
                <span>👑 펫로그 PRO</span>
                <span>• 전문 유료 케어</span>
              </span>
            </div>
            <span class="text-[11px] text-amber-300 font-semibold">1:1 맞춤 서비스</span>
          </div>

          <div>
            <h3 class="font-black text-base text-white">수의사 1:1 심층 상담 & 전문 훈련</h3>
            <p class="text-xs text-gray-300 mt-0.5">정밀 진단이 필요할 때 검증된 전문가와 1:1로 직접 연결됩니다.</p>
          </div>

          <div class="grid grid-cols-2 gap-2 pt-1">
            <div onclick="openProServiceModal('24시 수의사 1:1 비대면 화상/채팅 상담', '29,000원 (회당)', '🩺 전문 수의사의 임상 진단 소견서 및 약물 복용 가이드 제공')" class="bg-white/10 hover:bg-white/15 p-3 rounded-xl border border-white/10 cursor-pointer transition-all">
              <div class="text-xl mb-1">🩺</div>
              <h4 class="font-bold text-xs text-white">24시 수의사 1:1 상담</h4>
              <p class="text-[10px] text-amber-300 font-semibold mt-0.5">29,000원 / 회</p>
              <p class="text-[9px] text-gray-400 mt-1">대학병원급 정밀 소견서</p>
            </div>

            <div onclick="openProServiceModal('1급 반려견 전문 훈련사 1:1 방문 맞춤 교육', '99,000원 (회당)', '🎓 짖음, 분리불안, 공격성 전문 훈련사의 자택 방문 1:1 솔루션')" class="bg-white/10 hover:bg-white/15 p-3 rounded-xl border border-white/10 cursor-pointer transition-all">
              <div class="text-xl mb-1">🎓</div>
              <h4 class="font-bold text-xs text-white">1급 훈련사 방문 교육</h4>
              <p class="text-[10px] text-amber-300 font-semibold mt-0.5">99,000원 / 회</p>
              <p class="text-[9px] text-gray-400 mt-1">자택 방문 행동교정</p>
            </div>
          </div>
        </div>"""

if '<!-- [PAID PRO SERVICES]' not in html:
    html = html.replace('<!-- [PRIORITY 4] DOCTOR CHART PREVIEW', pro_services_html + '\n\n        <!-- [PRIORITY 4] DOCTOR CHART PREVIEW')

# 3. Add Free Trial Limit Reached Modal & PRO Modal
trial_modal_html = """    <!-- ================= Modal: Free Trial Limit Reached ================= -->
    <div id="modal-trial-limit" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white dark:bg-neutral-900 rounded-3xl p-6 space-y-4 border border-gray-200 dark:border-neutral-800 animate-slide-up text-left shadow-2xl">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-amber-100 dark:bg-amber-950/80 text-amber-600 flex items-center justify-center text-sm font-black">
              🎁
            </div>
            <h3 class="font-black text-sm text-gray-900 dark:text-white">1회 무료 체험 완료</h3>
          </div>
          <button onclick="closeTrialLimitModal()" class="p-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800 text-gray-400">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <div class="text-center py-2">
          <div class="w-16 h-16 rounded-full bg-indigo-50 dark:bg-indigo-950/60 mx-auto flex items-center justify-center text-3xl mb-3 shadow-inner">
            🔒
          </div>
          <h4 id="limit-feature-name" class="font-bold text-sm text-gray-900 dark:text-white">비회원 무료 체험 1회를 모두 사용하셨습니다</h4>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1.5">
            <strong>카카오 / 구글 1초 회원가입</strong>만 하시면<br>
            AI 사진 진단, 멍냥 궁합, 닥터 차트 등<br>
            <span class="text-indigo-600 dark:text-indigo-400 font-bold">모든 핵심 기능을 평생 무제한 무료</span>로 이용하실 수 있습니다!
          </p>
        </div>

        <!-- Social Buttons -->
        <div class="space-y-2 pt-1">
          <button onclick="closeTrialLimitModal(); loginWithKakao();" class="w-full py-3 px-4 rounded-xl bg-[#FEE500] hover:bg-[#FDD835] text-[#191919] font-bold text-xs flex items-center justify-center gap-2.5 shadow-sm transition-transform active:scale-98">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3C6.477 3 2 6.477 2 10.8c0 2.8 1.88 5.25 4.7 6.6l-.96 3.53c-.08.31.25.56.51.38l4.24-2.82c.49.07.99.11 1.51.11 5.523 0 10-3.477 10-7.8S17.523 3 12 3z"/>
            </svg>
            <span>카카오로 1초 가입하고 무제한 무료 이용</span>
          </button>

          <button onclick="closeTrialLimitModal(); loginWithGoogle();" class="w-full py-3 px-4 rounded-xl bg-white dark:bg-neutral-800 hover:bg-gray-50 dark:hover:bg-neutral-700 text-gray-800 dark:text-white font-bold text-xs flex items-center justify-center gap-2.5 border border-gray-300 dark:border-neutral-700 shadow-sm transition-transform active:scale-98">
            <svg class="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span>Google 계정으로 무제한 무료 이용</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ================= Modal: PRO Paid Feature ================= -->
    <div id="modal-pro-service" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-neutral-900 text-white rounded-3xl p-6 space-y-4 border border-amber-500/40 animate-slide-up text-left shadow-2xl">
        <div class="flex justify-between items-center border-b border-neutral-800 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-xl">👑</span>
            <h3 class="font-black text-sm text-amber-400">펫로그 PRO 유료 서비스</h3>
          </div>
          <button onclick="closeProServiceModal()" class="p-1.5 rounded-full hover:bg-neutral-800 text-gray-400">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <div class="space-y-2">
          <h4 id="pro-modal-title" class="font-bold text-base text-white">24시 수의사 1:1 상담</h4>
          <p id="pro-modal-desc" class="text-xs text-gray-300">전문 수의사의 임상 진단 소견서 및 약물 복용 가이드 제공</p>
          <div class="p-3 bg-neutral-800 rounded-xl border border-neutral-700 flex items-center justify-between">
            <span class="text-xs text-gray-400">이용 요금</span>
            <span id="pro-modal-price" class="text-sm font-black text-amber-400">29,000원</span>
          </div>
        </div>

        <div class="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-[11px] text-amber-200">
          💡 <strong>안내</strong>: 일반 가입 회원은 AI 사진 검진, 멍냥 궁합, 닥터 차트 PDF가 100% 무료이며, 전문 1:1 수의사 상담 및 방문 훈련사만 유료 결제로 진행됩니다.
        </div>

        <button onclick="requestProServiceOrder()" class="w-full py-3 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 text-black font-black text-xs shadow-lg hover:opacity-95 transition-all">
          전문가 1:1 매칭 신청하기
        </button>
      </div>
    </div>"""

if 'id="modal-trial-limit"' not in html:
    html = html.replace('<!-- ================= MODALS ================= -->', '<!-- ================= MODALS ================= -->\n' + trial_modal_html)

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated with Free Trial & Paid Tier Modals.")
