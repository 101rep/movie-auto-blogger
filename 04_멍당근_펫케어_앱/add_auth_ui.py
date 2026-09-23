import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"
app_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\app.js"

with open(index_file, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Google GSI Script to head if not present
if 'accounts.google.com/gsi/client' not in html:
    html = html.replace('</head>', """  <!-- Google Identity Services (Google One-Tap / Sign-In) -->
  <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>""")

# 2. Add Login trigger button to App Header
if 'id="btn-header-auth"' not in html:
    old_header_right = """        <!-- AI Instant Scanner Quick Button -->
        <button onclick="switchTab('ai')" class="flex items-center gap-1 px-2.5 py-1 bg-violet-50 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400 border border-violet-200 dark:border-violet-900/50 rounded-full text-xs font-semibold hover:scale-105 transition-transform">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
          <span>무료 AI검사</span>
        </button>"""
    
    new_header_right = """        <!-- Login Profile / Auth Trigger Button -->
        <button id="btn-header-auth" onclick="openAuthModal()" class="flex items-center gap-1.5 px-3 py-1 bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-900/60 rounded-full text-xs font-bold hover:scale-105 transition-transform">
          <i data-lucide="log-in" class="w-3.5 h-3.5"></i>
          <span id="header-auth-label">로그인</span>
        </button>"""
    html = html.replace(old_header_right, new_header_right)

# 3. Add Settings Account Center Card with Login/Logout dynamic state
old_account_center = """        <div class="bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-4 mb-3 space-y-2">
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
        </div>"""

new_account_center = """        <!-- Dynamic User Profile Account Box -->
        <div id="settings-user-box" class="bg-gradient-to-r from-indigo-50 to-violet-50 dark:from-neutral-900 dark:to-neutral-900 border border-indigo-100 dark:border-neutral-800 rounded-2xl p-4 mb-3 shadow-sm">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div id="user-avatar-badge" class="w-12 h-12 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xl font-bold shadow-md overflow-hidden">
                🐶
              </div>
              <div>
                <div class="flex items-center gap-1.5">
                  <span id="user-display-name" class="font-bold text-sm text-gray-900 dark:text-white">게스트 보호자님</span>
                  <span id="user-provider-badge" class="text-[10px] px-2 py-0.5 rounded-full bg-gray-200 dark:bg-neutral-800 text-gray-600 dark:text-gray-300 font-semibold">비회원</span>
                </div>
                <p id="user-email-text" class="text-[11px] text-gray-500 mt-0.5">로그인하고 닥터차트 클라우드 동기화</p>
              </div>
            </div>
            <button id="btn-settings-auth" onclick="openAuthModal()" class="px-3 py-1.5 rounded-xl bg-indigo-600 text-white text-xs font-bold shadow-sm hover:bg-indigo-700">
              로그인
            </button>
          </div>
        </div>"""

html = html.replace(old_account_center, new_account_center)

# 4. Add Auth Login Modal
auth_modal_html = """    <!-- ================= Modal: Social Auth (Kakao & Google) ================= -->
    <div id="modal-auth" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white dark:bg-neutral-900 rounded-3xl p-6 space-y-5 border border-gray-200 dark:border-neutral-800 animate-slide-up text-left shadow-2xl">
        
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white text-sm">
              🐾
            </div>
            <h3 class="font-black text-base text-gray-900 dark:text-white">간편 소셜 로그인</h3>
          </div>
          <button onclick="closeAuthModal()" class="p-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800 text-gray-400">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>

        <div class="text-center py-2">
          <div class="w-16 h-16 rounded-full bg-indigo-50 dark:bg-indigo-950/60 mx-auto flex items-center justify-center text-3xl mb-3 shadow-inner">
            🐶
          </div>
          <h4 class="font-bold text-sm text-gray-900 dark:text-white">펫로그 AI 시작하기</h4>
          <p class="text-xs text-gray-500 mt-1">소셜 계정으로 1초 만에 가입하고<br>우리 아이 건강 기록을 안전하게 보관하세요.</p>
        </div>

        <!-- Social Buttons -->
        <div class="space-y-2.5">
          <!-- Kakao Login Button -->
          <button onclick="loginWithKakao()" class="w-full py-3 px-4 rounded-xl bg-[#FEE500] hover:bg-[#FDD835] text-[#191919] font-bold text-xs flex items-center justify-center gap-2.5 shadow-sm transition-transform active:scale-98">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3C6.477 3 2 6.477 2 10.8c0 2.8 1.88 5.25 4.7 6.6l-.96 3.53c-.08.31.25.56.51.38l4.24-2.82c.49.07.99.11 1.51.11 5.523 0 10-3.477 10-7.8S17.523 3 12 3z"/>
            </svg>
            <span>카카오로 1초 시작하기</span>
          </button>

          <!-- Google Login Button -->
          <button onclick="loginWithGoogle()" class="w-full py-3 px-4 rounded-xl bg-white dark:bg-neutral-800 hover:bg-gray-50 dark:hover:bg-neutral-700 text-gray-800 dark:text-white font-bold text-xs flex items-center justify-center gap-2.5 border border-gray-300 dark:border-neutral-700 shadow-sm transition-transform active:scale-98">
            <svg class="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span>Google 계정으로 계속하기</span>
          </button>
        </div>

        <div class="pt-2 text-center border-t border-gray-100 dark:border-neutral-800">
          <button onclick="closeAuthModal()" class="text-[11px] text-gray-400 hover:text-gray-600 underline">
            로그인 없이 둘러보기
          </button>
        </div>
      </div>
    </div>"""

if 'id="modal-auth"' not in html:
    html = html.replace('<!-- ================= MODALS ================= -->', '<!-- ================= MODALS ================= -->\n' + auth_modal_html)

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html for Social Login.")
