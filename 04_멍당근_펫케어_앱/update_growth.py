# -*- coding: utf-8 -*-
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Update index.html
html_path = os.path.join(APP_DIR, 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Viral Banner in Home
if '<!-- Viral AI Pet Face' not in html:
    target = '<!-- Quick 3-Second V-Check Banner -->'
    viral_banner = '''<!-- Viral AI Pet Face & MBTI Card Banner (Growth Hack) -->
        <div onclick="openViralModal()" class="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white rounded-2xl p-4 cursor-pointer shadow-md hover:opacity-95 transition-all flex items-center justify-between relative overflow-hidden">
          <div class="space-y-1 z-10">
            <div class="flex items-center gap-1 text-[11px] font-bold bg-white/20 w-fit px-2 py-0.5 rounded-full">
              <span>🔥 SNS 화제</span>
              <span>• AI 관상 & MBTI 분석</span>
            </div>
            <h3 class="font-black text-base">우리 아이 관상 & 멍냥 MBTI는?</h3>
            <p class="text-xs text-pink-100">사진 1장으로 인스타 스토리 공유 카드 1초 완성!</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center text-2xl shrink-0 z-10">
            ✨
          </div>
        </div>

        <!-- Quick 3-Second V-Check Banner -->'''
    html = html.replace(target, viral_banner)

# Viral Modal in index.html
if 'id="modal-viral-mbti"' not in html:
    modal_code = '''
    <!-- Modal: Viral AI Face & MBTI Result -->
    <div id="modal-viral-mbti" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white dark:bg-neutral-900 rounded-3xl p-5 space-y-4 border border-gray-200 dark:border-neutral-800 animate-slide-up text-center">
        <div class="flex justify-between items-center border-b border-gray-100 dark:border-neutral-800 pb-2">
          <span class="text-xs font-bold text-pink-600 dark:text-pink-400">🐾 AI 멍냥 관상 & MBTI 분석</span>
          <button onclick="closeViralModal()" class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Share Card Preview -->
        <div id="mbti-share-card" class="bg-gradient-to-tr from-pink-500 via-purple-600 to-indigo-600 rounded-2xl p-5 text-white shadow-xl space-y-3 relative overflow-hidden text-left">
          <div class="flex justify-between items-start">
            <span class="text-2xl">👑</span>
            <span class="text-[10px] bg-white/20 px-2 py-0.5 rounded-full font-bold">MBTI: ENFP (재롱둥이형)</span>
          </div>
          <div>
            <h3 class="text-xl font-black">초코의 관상 분석</h3>
            <p class="text-xs text-pink-100 mt-0.5">"평생 사랑받을 사랑둥이 눈망울과 간식 레이더형 코"</p>
          </div>
          <div class="bg-black/30 backdrop-blur-sm p-3 rounded-xl space-y-1 text-xs">
            <p>💖 <b>친화력</b>: 99점 (처음 본 사람도 1초 만에 꼬리 흔듦)</p>
            <p>🍖 <b>식탐력</b>: 95점 (간식 봉지 소리에 번개 반응)</p>
            <p>👑 <b>자기애</b>: 92점 (거울 보면 자기가 예쁜 줄 앎)</p>
          </div>
          <div class="text-right text-[10px] text-pink-200 font-mono">
            #펫로그AI #반려견MBTI #인스타공유
          </div>
        </div>

        <div class="space-y-2 pt-1">
          <button onclick="shareToInstagram()" class="w-full py-3 bg-gradient-to-r from-pink-500 to-rose-500 hover:opacity-95 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-lg shadow-pink-500/30">
            <i data-lucide="instagram" class="w-4 h-4"></i>
            <span>인스타그램 스토리 / 카카오톡 공유하기</span>
          </button>
          <button onclick="closeViralModal()" class="w-full py-2 bg-gray-100 dark:bg-neutral-800 text-gray-700 dark:text-gray-300 font-semibold rounded-xl text-xs">
            닫기
          </button>
        </div>
      </div>
    </div>
'''
    html = html.replace('<!-- Modal: Send Doctor Chart', modal_code + '\n    <!-- Modal: Send Doctor Chart')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated index.html successfully')

# 2. Update app.js for Services Coming Soon + Viral logic
js_path = os.path.join(APP_DIR, 'app.js')
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

new_render_service = '''// O2O Services (Coming Soon & Pre-registration Strategy)
function renderServiceDetail() {
  const container = document.getElementById('service-detail-container');
  if (!container) return;

  const titles = {
    pickup: { name: '픽업 이동 (병원/미용/유치원)', icon: '🚗', bg: 'bg-blue-500', desc: '바쁜 보호자님을 대신해 병원/미용실까지 안전하게 왕복 이동' },
    education: { name: '전문 훈련사 방문 교육', icon: '🎓', bg: 'bg-purple-500', desc: '국가 공인 행동교정 전문가 1:1 방문 훈련 & 솔루션 카드' },
    care: { name: '자택 방문 전문 펫시터', icon: '🏠', bg: 'bg-emerald-500', desc: '검증된 펫시터가 집으로 방문해 1:1 밀착 케어 및 라이브 리포트' },
    walk: { name: '전문 도그워커 산책 대행', icon: '🦮', bg: 'bg-amber-500', desc: 'GPS 실시간 산책 경로 추적 & 배변 사진 실시간 안심 전송' }
  };

  const cur = titles[currentServiceTab] || titles.pickup;

  container.innerHTML = `
    <!-- Coming Soon & Pre-Registration Card -->
    <div class="bg-gradient-to-br from-neutral-900 to-neutral-800 border border-neutral-700 text-white rounded-2xl p-5 space-y-4 shadow-xl relative overflow-hidden">
      <div class="absolute -right-6 -bottom-6 opacity-10 text-9xl">✨</div>
      
      <div class="flex items-center gap-2">
        <span class="text-2xl">${cur.icon}</span>
        <div>
          <div class="flex items-center gap-1.5">
            <h3 class="font-bold text-sm">${cur.name}</h3>
            <span class="text-[10px] bg-indigo-500/30 text-indigo-300 border border-indigo-400/40 px-2 py-0.5 rounded-full font-bold">오픈 준비 중</span>
          </div>
          <p class="text-xs text-neutral-300 mt-0.5">${cur.desc}</p>
        </div>
      </div>

      <!-- Pre-registration Benefits -->
      <div class="bg-white/5 border border-white/10 p-3.5 rounded-xl space-y-2 text-xs">
        <p class="font-bold text-amber-300 flex items-center gap-1">
          <span>🎁 사전 알림 신청자 한정 특별 혜택</span>
        </p>
        <ul class="text-[11px] text-neutral-300 space-y-1 list-disc list-inside">
          <li>우리 동네 서비스 런칭 시 <b>첫 이용 10,000원 할인 쿠폰</b> 즉시 지급</li>
          <li>우선 매칭 VIP 프리패스 부여 (피크타임 우선 배정)</li>
        </ul>
      </div>

      <!-- User Action 1: Customer Pre-registration -->
      <div class="space-y-2">
        <div class="flex gap-2">
          <input type="text" id="pre-reg-region" placeholder="거주 지역 (예: 서울 강남구 역삼동)" class="flex-1 text-xs p-3 rounded-xl bg-neutral-800 border border-neutral-700 text-white placeholder-neutral-500 focus:outline-none focus:border-indigo-500">
          <button onclick="submitPreRegistration('${cur.name}')" class="px-4 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs shrink-0 shadow-lg shadow-indigo-600/30">
            사전 알림 받기
          </button>
        </div>
        <p class="text-[10px] text-neutral-400 text-center">신청 인원이 100명이 넘는 동네부터 순차적으로 오픈됩니다.</p>
      </div>

      <!-- User Action 2: Partner/Sitter Pre-application -->
      <div class="pt-3 border-t border-neutral-700 flex items-center justify-between">
        <span class="text-[11px] text-neutral-300">전문 훈련사/시터/드라이버이신가요?</span>
        <button onclick="openPartnerApplication()" class="text-xs text-emerald-400 font-bold hover:underline flex items-center gap-0.5">
          파트너 사전 등록 >
        </button>
      </div>
    </div>
  `;

  lucide.createIcons();
}

function submitPreRegistration(serviceName) {
  const region = document.getElementById('pre-reg-region').value.trim();
  if (!region) {
    alert('거주하시는 지역(동/구)을 입력해주세요!');
    return;
  }
  alert(`🎉 [${region}] 지역 ${serviceName} 사전 알림 등록이 완료되었습니다!\n서비스 오픈 시 10,000원 할인 쿠폰과 함께 가장 먼저 연락드리겠습니다.`);
  document.getElementById('pre-reg-region').value = '';
}

function openPartnerApplication() {
  const license = prompt("보유하신 자격증 또는 전문 분야를 입력해주세요:\n(예: 반려동물행동교정사, 펫시터 수료, 운전경력 5년 등)");
  if (license) {
    alert("💼 [파트너 지원 완료] 전문 파트너 검증 팀에서 등록 서류 안내 문자를 발송해 드리겠습니다.");
  }
}

function openViralModal() {
  const modal = document.getElementById('modal-viral-mbti');
  if (modal) modal.classList.remove('hidden');
  lucide.createIcons();
}

function closeViralModal() {
  const modal = document.getElementById('modal-viral-mbti');
  if (modal) modal.classList.add('hidden');
}

function shareToInstagram() {
  if (navigator.share) {
    navigator.share({
      title: '초코의 AI 관상 & MBTI 분석 결과',
      text: '우리 아이는 ENFP 재롱둥이형! 펫로그 AI에서 확인해보세요 🐾',
      url: window.location.href
    }).catch(() => {});
  } else {
    navigator.clipboard.writeText(window.location.href);
    alert('📋 [공유 링크 복사 완료] 인스타그램 스토리나 단톡방에 붙여넣어 공유하세요!');
  }
}
'''

# Replace old renderServiceDetail in app.js
if 'function renderServiceDetail()' in js:
    parts = js.split('function renderServiceDetail()')
    js_header = parts[0]
    js = js_header + new_render_service

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print('Updated app.js successfully')