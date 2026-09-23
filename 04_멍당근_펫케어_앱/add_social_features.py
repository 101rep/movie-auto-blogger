# -*- coding: utf-8 -*-
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Update index.html
html_path = os.path.join(APP_DIR, 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add Pet Compatibility Banner to Home if not present
if '<!-- AI Pet Compatibility & Social Banner -->' not in html:
    target = '<!-- Quick Service Navigation (O2O) -->'
    social_banner = '''<!-- AI Pet Compatibility & Social Banner -->
        <div class="grid grid-cols-2 gap-2">
          <div onclick="openCompatibilityModal()" class="bg-gradient-to-br from-rose-500 to-pink-600 text-white rounded-2xl p-3.5 cursor-pointer shadow-md hover:opacity-95 transition-all space-y-1 relative overflow-hidden">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold bg-white/20 px-2 py-0.5 rounded-full">💖 케미 분석</span>
              <span class="text-xl">🐶🐱</span>
            </div>
            <h4 class="font-black text-sm pt-1">멍냥 궁합 테스트</h4>
            <p class="text-[10px] text-rose-100">친구네 강아지와 우리 아이 성격 궁합은 몇 점?</p>
          </div>

          <div onclick="openDogTalkModal()" class="bg-gradient-to-br from-emerald-500 to-teal-600 text-white rounded-2xl p-3.5 cursor-pointer shadow-md hover:opacity-95 transition-all space-y-1 relative overflow-hidden">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold bg-white/20 px-2 py-0.5 rounded-full">💬 소통 번역</span>
              <span class="text-xl">🐾</span>
            </div>
            <h4 class="font-black text-sm pt-1">카밍 시그널 사전</h4>
            <p class="text-[10px] text-emerald-100">꼬리 흔들기, 하품... 무슨 뜻일까? AI 번역기</p>
          </div>
        </div>

        <!-- Dongne Dog Friends Social Lounge -->
        <div class="bg-white dark:bg-neutral-900 border border-gray-200 dark:border-neutral-800 rounded-2xl p-4 shadow-sm space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1.5 font-bold text-sm text-gray-800 dark:text-gray-100">
              <span class="text-base">🐕</span>
              <span>우리 동네 산책 친구 & 궁합 매칭</span>
            </div>
            <span class="text-[11px] text-indigo-600 dark:text-indigo-400 font-semibold cursor-pointer" onclick="alert('동네 친구 초대 링크가 복사되었습니다!')">초대하기 +</span>
          </div>

          <div id="dog-friends-lounge" class="space-y-2 text-xs">
            <!-- Dynamic Friend List -->
            <div class="p-2.5 bg-gray-50 dark:bg-neutral-800/60 rounded-xl border border-gray-100 dark:border-neutral-800 flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <div class="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-950 flex items-center justify-center text-xl">
                  🐩
                </div>
                <div>
                  <div class="flex items-center gap-1.5">
                    <span class="font-bold text-gray-800 dark:text-gray-200">뽀삐 (토이푸들, 2세)</span>
                    <span class="text-[9px] bg-rose-100 dark:bg-rose-950 text-rose-600 dark:text-rose-400 px-1.5 py-0.2 rounded-full font-bold">초코와 궁합 96%</span>
                  </div>
                  <p class="text-[11px] text-gray-500 mt-0.5">"오늘 저녁 7시 역삼공원 산책할 친구 찾아요!"</p>
                </div>
              </div>
              <button onclick="requestWalkMate('뽀삐')" class="px-2.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-[10px] font-bold shrink-0">
                산책 신청
              </button>
            </div>

            <div class="p-2.5 bg-gray-50 dark:bg-neutral-800/60 rounded-xl border border-gray-100 dark:border-neutral-800 flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-950 flex items-center justify-center text-xl">
                  🐕‍🦺
                </div>
                <div>
                  <div class="flex items-center gap-1.5">
                    <span class="font-bold text-gray-800 dark:text-gray-200">몽이 (골든리트리버, 4세)</span>
                    <span class="text-[9px] bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 px-1.5 py-0.2 rounded-full font-bold">초코와 궁합 88%</span>
                  </div>
                  <p class="text-[11px] text-gray-500 mt-0.5">"순하고 친구 좋아하는 성격이에요 🐾"</p>
                </div>
              </div>
              <button onclick="requestWalkMate('몽이')" class="px-2.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-[10px] font-bold shrink-0">
                산책 신청
              </button>
            </div>
          </div>
        </div>

        <!-- Quick Service Navigation (O2O) -->'''
    html = html.replace(target, social_banner)

# Add Compatibility Modal & Dog Talk Modal if not present
if 'id="modal-compatibility"' not in html:
    modals_code = '''
    <!-- Modal: AI Pet Compatibility Scanner -->
    <div id="modal-compatibility" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white dark:bg-neutral-900 rounded-3xl p-5 space-y-4 border border-gray-200 dark:border-neutral-800 animate-slide-up text-center">
        <div class="flex justify-between items-center border-b border-gray-100 dark:border-neutral-800 pb-2">
          <span class="text-xs font-bold text-rose-600 dark:text-rose-400">💖 AI 반려동물 케미 & 궁합 분석</span>
          <button onclick="closeCompatibilityModal()" class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <div class="space-y-3 text-left">
          <div class="flex items-center justify-center gap-3 py-2">
            <div class="text-center">
              <div class="w-14 h-14 rounded-full bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center text-3xl border-2 border-indigo-500">
                🐕
              </div>
              <span class="text-xs font-bold mt-1 block">우리 초코</span>
            </div>
            <div class="text-2xl font-black text-rose-500 animate-bounce">❤️</div>
            <div class="text-center">
              <select id="compat-partner-select" onchange="calcCompatibility()" class="w-20 text-xs p-1 rounded-lg bg-gray-100 dark:bg-neutral-800 border border-gray-300 dark:border-neutral-700">
                <option value="poodle">토이푸들 뽀삐</option>
                <option value="retriever">리트리버 몽이</option>
                <option value="cat_luna">고양이 루나</option>
                <option value="corgi">웰시코기 둥이</option>
              </select>
              <span class="text-xs font-bold mt-1 block">친구 아이</span>
            </div>
          </div>

          <!-- Compatibility Result Card -->
          <div id="compat-result-card" class="bg-gradient-to-br from-rose-500 to-purple-600 rounded-2xl p-4 text-white space-y-2 shadow-lg">
            <div class="flex justify-between items-center">
              <span class="text-xs font-bold bg-white/20 px-2 py-0.5 rounded-full">케미 지수</span>
              <span class="text-2xl font-black" id="compat-score">96점</span>
            </div>
            <h4 class="font-bold text-sm" id="compat-title">"찰떡궁합! 평생 단짝 베프"</h4>
            <p class="text-xs text-rose-100 leading-relaxed" id="compat-desc">
              초코의 활발한 성격과 뽀삐의 다정한 성향이 완벽히 조화를 이룹니다. 함께 산책하면 에너지를 기분 좋게 발산할 수 있습니다.
            </p>
            <div class="text-[10px] text-rose-200 bg-black/20 p-2 rounded-lg mt-2">
              💡 <b>합사/산책 꿀팁</b>: 첫 만남 때는 좁은 공간보다 넓은 공원에서 나란히 걷는 평행 산책부터 시작하세요!
            </div>
          </div>

          <button onclick="shareCompatibility()" class="w-full py-3 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-md">
            <span>친구에게 궁합 결과 공유하기 (인스타/카톡)</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Dog Calming Signals & Communication Translator -->
    <div id="modal-dogtalk" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white dark:bg-neutral-900 rounded-3xl p-5 space-y-4 border border-gray-200 dark:border-neutral-800 animate-slide-up max-h-[85vh] overflow-y-auto text-left">
        <div class="flex justify-between items-center border-b border-gray-100 dark:border-neutral-800 pb-2">
          <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-600 dark:text-emerald-400">
            <span>💬 강아지 언어(카밍 시그널) AI 번역 백과</span>
          </div>
          <button onclick="closeDogTalkModal()" class="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <p class="text-xs text-gray-500 leading-relaxed">
          강아지는 몸짓과 행동으로 끊임없이 이야기합니다. 지금 우리 아이가 보내는 신호를 확인해보세요!
        </p>

        <!-- Signal Cards List -->
        <div class="space-y-2.5 text-xs">
          <div class="p-3 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/40 space-y-1">
            <div class="flex items-center justify-between font-bold text-emerald-800 dark:text-emerald-200">
              <span>🙇 상체를 낮추고 엉덩이를 드는 자세 (플레이 바우)</span>
              <span class="text-[10px] bg-emerald-200 dark:bg-emerald-900 px-1.5 py-0.2 rounded font-bold">놀자!</span>
            </div>
            <p class="text-[11px] text-emerald-950 dark:text-emerald-300">
              "나 너랑 친구하고 싶어! 신나게 같이 뛰어놀래?" 라는 가장 대표적인 우호 신호입니다.
            </p>
          </div>

          <div class="p-3 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/40 space-y-1">
            <div class="flex items-center justify-between font-bold text-amber-800 dark:text-amber-200">
              <span>🥱 갑자기 하품을 하거나 시선을 피함</span>
              <span class="text-[10px] bg-amber-200 dark:bg-amber-900 px-1.5 py-0.2 rounded font-bold">긴장/진정</span>
            </div>
            <p class="text-[11px] text-amber-950 dark:text-amber-300">
              "나 지금 조금 긴장했어. 우리 서로 흥분을 가라앉히자" 라는 상대방을 안심시키는 평화의 신호입니다.
            </p>
          </div>

          <div class="p-3 rounded-2xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900/40 space-y-1">
            <div class="flex items-center justify-between font-bold text-blue-800 dark:text-blue-200">
              <span>👅 코를 날름 핥거나 자기 입술을 핥음</span>
              <span class="text-[10px] bg-blue-200 dark:bg-blue-900 px-1.5 py-0.2 rounded font-bold">불안/스트레스</span>
            </div>
            <p class="text-[11px] text-blue-950 dark:text-blue-300">
              보호자에게 혼나거나 낯선 환경에 있을 때 스트레스를 완화하려는 행동입니다. 부드럽게 다독여주세요.
            </p>
          </div>
        </div>

        <button onclick="alert('📸 사진 촬영 시 AI가 카밍 시그널을 자동 판별합니다!')" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-md">
          <i data-lucide="camera" class="w-4 h-4"></i>
          <span>실시간 사진 찍어 행동 번역하기</span>
        </button>
      </div>
    </div>
'''
    html = html.replace('<!-- Modal: Viral AI Face', modals_code + '\n    <!-- Modal: Viral AI Face')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated index.html with Compatibility & DogTalk modals successfully')

# 2. Update app.js
js_path = os.path.join(APP_DIR, 'app.js')
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

social_js = '''
// AI Compatibility Scanner Logic
function openCompatibilityModal() {
  const modal = document.getElementById('modal-compatibility');
  if (modal) modal.classList.remove('hidden');
  calcCompatibility();
  lucide.createIcons();
}

function closeCompatibilityModal() {
  const modal = document.getElementById('modal-compatibility');
  if (modal) modal.classList.add('hidden');
}

function calcCompatibility() {
  const select = document.getElementById('compat-partner-select');
  const partner = select ? select.value : 'poodle';

  const data = {
    poodle: { score: '96점', title: '"찰떡궁합! 평생 단짝 베프"', desc: '초코의 활발한 성격과 뽀삐의 다정한 성향이 완벽히 조화를 이룹니다. 산책할 때 최고의 짝꿍입니다.' },
    retriever: { score: '88점', title: '"든든한 맏형과 막내 케미"', desc: '대형견 몽이의 의젓함이 초코에게 큰 안정감을 줍니다. 서로 질투하지 않고 잘 어울려요.' },
    cat_luna: { score: '72점', title: '"밀당하는 톰과 제리"', desc: '고양이 루나의 독립적인 성향에 맞춰 초코가 거리를 조절해 주어야 합니다. 간식을 함께 급여하며 친해지세요.' },
    corgi: { score: '91점', title: '"에너지 폭발! 우다다 콤비"', desc: '활동량이 넘치는 두 아이가 만나면 지치지 않고 신나게 터그놀이와 달리기 산책을 즐길 수 있습니다.' }
  };

  const item = data[partner] || data.poodle;
  const scoreEl = document.getElementById('compat-score');
  const titleEl = document.getElementById('compat-title');
  const descEl = document.getElementById('compat-desc');

  if (scoreEl) scoreEl.textContent = item.score;
  if (titleEl) titleEl.textContent = item.title;
  if (descEl) descEl.textContent = item.desc;
}

function shareCompatibility() {
  alert('🎉 [공유 완료] 초코와 친구 강아지의 케미 지수 카드가 인스타 스토리/카톡 공유용으로 복사되었습니다!');
}

// Dog Talk Calming Signals Logic
function openDogTalkModal() {
  const modal = document.getElementById('modal-dogtalk');
  if (modal) modal.classList.remove('hidden');
  lucide.createIcons();
}

function closeDogTalkModal() {
  const modal = document.getElementById('modal-dogtalk');
  if (modal) modal.classList.add('hidden');
}

function requestWalkMate(friendName) {
  alert(`🐕 [산책 신청 완료] ${friendName} 보호자님께 산책 번개 요청을 보냈습니다!\n상대방이 수락하면 채팅방이 연결됩니다.`);
}
'''

if 'function openCompatibilityModal()' not in js:
    js += '\n' + social_js

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print('Updated app.js with social features successfully')