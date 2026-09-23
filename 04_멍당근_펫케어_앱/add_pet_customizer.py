import os

index_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\index.html"
app_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\app.js"

with open(index_file, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Home Welcome Section with dynamic Profile Box & Edit Button
old_welcome_sec = """        <!-- Bright Welcome Title -->
        <div class="pt-1 px-1">
          <div class="flex items-center gap-2">
            <span class="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 font-bold">🐶 우리 아이 맞춤 케어</span>
            <span class="text-xs text-slate-400">말티즈 • 3세 초코</span>
          </div>
          <h2 class="text-2xl font-black text-slate-900 mt-1 leading-snug">
            초코와 함께하는<br><span class="text-blue-600">신나는 건강 케어 시간~</span> 🧸
          </h2>
        </div>"""

new_welcome_sec = """        <!-- Dynamic Pet Profile & Custom Welcome Header -->
        <div class="pet-card rounded-3xl p-4 bg-gradient-to-r from-blue-50/70 via-sky-50/40 to-indigo-50/70 border border-blue-100/80 shadow-sm">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <!-- Clickable Pet Avatar -->
              <div onclick="openPetProfileModal()" class="relative cursor-pointer group">
                <div id="home-pet-avatar" class="w-16 h-16 rounded-2xl bg-white border-2 border-blue-400/60 shadow-md flex items-center justify-center text-3xl overflow-hidden group-hover:scale-105 transition-transform">
                  🐕
                </div>
                <div class="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px] shadow border-2 border-white">
                  📷
                </div>
              </div>

              <!-- Dynamic Name & Breed Info -->
              <div class="space-y-0.5">
                <div class="flex items-center gap-1.5">
                  <span class="text-[10px] px-2 py-0.5 rounded-full bg-blue-600 text-white font-black">내 반려동물</span>
                  <span id="home-pet-subtext" class="text-xs font-bold text-slate-500">말티즈 • 3세 • 3.4kg</span>
                </div>
                <h2 id="home-welcome-title" class="text-lg font-black text-slate-900 leading-snug">
                  <span id="home-pet-name" class="text-blue-600">초코</span>와 함께하는<br>
                  신나는 건강 케어~ 🧸
                </h2>
              </div>
            </div>

            <!-- Profile Edit Trigger Button -->
            <button onclick="openPetProfileModal()" class="px-2.5 py-1.5 rounded-xl bg-white hover:bg-blue-50 text-blue-600 border border-blue-200 text-xs font-bold shadow-sm shrink-0 flex items-center gap-1 transition-transform active:scale-95">
              <i data-lucide="edit-3" class="w-3.5 h-3.5"></i>
              <span>아이 변경</span>
            </button>
          </div>
        </div>"""

html = html.replace(old_welcome_sec, new_welcome_sec)

# 2. Add Pet Profile Customizer Modal
pet_modal_html = """    <!-- ================= Modal: Pet Profile Registration & Customizer ================= -->
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

        <!-- Photo Selection -->
        <div class="text-center space-y-2 py-1">
          <div class="relative w-20 h-20 mx-auto">
            <div id="modal-preview-avatar" class="w-20 h-20 rounded-3xl bg-blue-50 border-2 border-blue-400 flex items-center justify-center text-4xl shadow-inner overflow-hidden">
              🐕
            </div>
            <label for="pet-photo-upload" class="absolute -bottom-1 -right-1 p-2 rounded-full bg-blue-600 text-white shadow-lg cursor-pointer hover:bg-blue-700 transition-transform active:scale-90" title="실제 사진 업로드">
              <i data-lucide="camera" class="w-4 h-4"></i>
            </label>
            <input type="file" id="pet-photo-upload" accept="image/*" onchange="handlePetPhotoUpload(event)" class="hidden">
          </div>
          <p class="text-[11px] text-slate-500">카메라 아이콘을 눌러 <strong>실제 갤러리 사진</strong>을 등록하세요</p>

          <!-- Quick Emoji Avatars -->
          <div class="flex justify-center gap-1.5 pt-1">
            <button onclick="selectEmojiAvatar('🐕')" class="w-8 h-8 rounded-xl bg-slate-50 hover:bg-blue-100 border text-lg flex items-center justify-center">🐕</button>
            <button onclick="selectEmojiAvatar('🐶')" class="w-8 h-8 rounded-xl bg-slate-50 hover:bg-blue-100 border text-lg flex items-center justify-center">🐶</button>
            <button onclick="selectEmojiAvatar('🐩')" class="w-8 h-8 rounded-xl bg-slate-50 hover:bg-blue-100 border text-lg flex items-center justify-center">🐩</button>
            <button onclick="selectEmojiAvatar('🐈')" class="w-8 h-8 rounded-xl bg-slate-50 hover:bg-blue-100 border text-lg flex items-center justify-center">🐈</button>
            <button onclick="selectEmojiAvatar('🐱')" class="w-8 h-8 rounded-xl bg-slate-50 hover:bg-blue-100 border text-lg flex items-center justify-center">🐱</button>
            <button onclick="selectEmojiAvatar('🐾')" class="w-8 h-8 rounded-xl bg-slate-50 hover:bg-blue-100 border text-lg flex items-center justify-center">🐾</button>
          </div>
        </div>

        <!-- Input Fields -->
        <div class="space-y-2.5 text-xs">
          <!-- Pet Name -->
          <div>
            <label class="font-black text-slate-700 block mb-1">우리 아이 이름 (필수) 🐾</label>
            <input type="text" id="input-pet-name" placeholder="예: 뽀삐, 몽이, 두부, 초코" class="w-full p-3 rounded-2xl border border-slate-200 bg-slate-50 font-bold focus:bg-white focus:border-blue-500 outline-none">
          </div>

          <!-- Pet Breed -->
          <div>
            <label class="font-black text-slate-700 block mb-1">견종 / 묘종 🐶</label>
            <input type="text" id="input-pet-breed" placeholder="예: 말티즈, 토이푸들, 포메라니안, 코숏" class="w-full p-3 rounded-2xl border border-slate-200 bg-slate-50 font-medium focus:bg-white focus:border-blue-500 outline-none">
          </div>

          <!-- Age & Weight -->
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="font-black text-slate-700 block mb-1">나이 🎂</label>
              <input type="text" id="input-pet-age" placeholder="예: 3세 (또는 6개월)" class="w-full p-3 rounded-2xl border border-slate-200 bg-slate-50 font-medium outline-none">
            </div>
            <div>
              <label class="font-black text-slate-700 block mb-1">체중 ⚖️</label>
              <input type="text" id="input-pet-weight" placeholder="예: 3.4kg" class="w-full p-3 rounded-2xl border border-slate-200 bg-slate-50 font-medium outline-none">
            </div>
          </div>

          <!-- Gender & Neutered -->
          <div>
            <label class="font-black text-slate-700 block mb-1">성별 & 중성화 🩺</label>
            <div class="grid grid-cols-3 gap-1.5 text-[11px] font-bold">
              <button type="button" onclick="selectPetGender(this, '남아 (중성화 O)')" class="pet-gender-btn py-2 rounded-xl border bg-slate-50 active">남아 (중성화 O)</button>
              <button type="button" onclick="selectPetGender(this, '여아 (중성화 O)')" class="pet-gender-btn py-2 rounded-xl border bg-slate-50">여아 (중성화 O)</button>
              <button type="button" onclick="selectPetGender(this, '미중성화')" class="pet-gender-btn py-2 rounded-xl border bg-slate-50">미중성화</button>
            </div>
          </div>
        </div>

        <!-- Save Button -->
        <button onclick="savePetProfile()" class="w-full py-3.5 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-black text-xs shadow-lg transition-transform active:scale-98">
          내 아이 정보 등록하고 앱 맞춤 완성 ✨
        </button>

      </div>
    </div>"""

if 'id="modal-pet-profile"' not in html:
    html = html.replace('<!-- ================= MODALS ================= -->', '<!-- ================= MODALS ================= -->\n' + pet_modal_html)

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated with dynamic pet profile customizer.")

# 3. Update app.js with Pet Profile Management Logic
with open(app_file, 'r', encoding='utf-8') as f:
    js = f.read()

pet_customizer_logic = """
// ================= 10. Dynamic Pet Profile Customizer =================
let currentPet = JSON.parse(localStorage.getItem('petlog_pet_profile')) || {
  name: '초코',
  breed: '말티즈',
  age: '3세',
  weight: '3.4kg',
  gender: '남아 (중성화 O)',
  avatar: '🐕',
  photoUrl: null
};

let tempUploadedPhoto = null;
let tempSelectedAvatar = '🐕';
let tempSelectedGender = '남아 (중성화 O)';

window.openPetProfileModal = function() {
  const modal = document.getElementById('modal-pet-profile');
  if (!modal) return;

  // Populate inputs with current pet data
  const nameInput = document.getElementById('input-pet-name');
  const breedInput = document.getElementById('input-pet-breed');
  const ageInput = document.getElementById('input-pet-age');
  const weightInput = document.getElementById('input-pet-weight');
  const previewAvatar = document.getElementById('modal-preview-avatar');

  if (nameInput) nameInput.value = currentPet.name || '';
  if (breedInput) breedInput.value = currentPet.breed || '';
  if (ageInput) ageInput.value = currentPet.age || '';
  if (weightInput) weightInput.value = currentPet.weight || '';
  
  tempSelectedAvatar = currentPet.avatar || '🐕';
  tempUploadedPhoto = currentPet.photoUrl || null;
  tempSelectedGender = currentPet.gender || '남아 (중성화 O)';

  if (previewAvatar) {
    if (tempUploadedPhoto) {
      previewAvatar.innerHTML = `<img src="${tempUploadedPhoto}" class="w-full h-full object-cover">`;
    } else {
      previewAvatar.textContent = tempSelectedAvatar;
    }
  }

  modal.classList.remove('hidden');
  if (window.lucide) lucide.createIcons();
};

window.closePetProfileModal = function() {
  const modal = document.getElementById('modal-pet-profile');
  if (modal) modal.classList.add('hidden');
};

window.handlePetPhotoUpload = function(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    tempUploadedPhoto = e.target.result;
    const previewAvatar = document.getElementById('modal-preview-avatar');
    if (previewAvatar) {
      previewAvatar.innerHTML = `<img src="${tempUploadedPhoto}" class="w-full h-full object-cover">`;
    }
  };
  reader.readAsDataURL(file);
};

window.selectEmojiAvatar = function(emoji) {
  tempUploadedPhoto = null;
  tempSelectedAvatar = emoji;
  const previewAvatar = document.getElementById('modal-preview-avatar');
  if (previewAvatar) {
    previewAvatar.innerHTML = emoji;
  }
};

window.selectPetGender = function(btn, gender) {
  tempSelectedGender = gender;
  document.querySelectorAll('.pet-gender-btn').forEach(b => {
    b.classList.remove('bg-blue-600', 'text-white');
    b.classList.add('bg-slate-50', 'text-slate-700');
  });
  btn.classList.add('bg-blue-600', 'text-white');
  btn.classList.remove('bg-slate-50', 'text-slate-700');
};

window.savePetProfile = function() {
  const name = document.getElementById('input-pet-name').value.trim();
  const breed = document.getElementById('input-pet-breed').value.trim() || '반려견';
  const age = document.getElementById('input-pet-age').value.trim() || '나이 미등록';
  const weight = document.getElementById('input-pet-weight').value.trim() || '체중 미등록';

  if (!name) {
    alert('반려동물의 이름을 입력해 주세요!');
    document.getElementById('input-pet-name').focus();
    return;
  }

  currentPet = {
    name: name,
    breed: breed,
    age: age,
    weight: weight,
    gender: tempSelectedGender,
    avatar: tempSelectedAvatar,
    photoUrl: tempUploadedPhoto
  };

  localStorage.setItem('petlog_pet_profile', JSON.stringify(currentPet));
  applyPetProfileToUI();
  closePetProfileModal();
  alert(`🎉 [${name}]의 맞춤 펫케어 앱으로 커스터마이징이 완료되었습니다! 🐾`);
};

function applyPetProfileToUI() {
  const homePetName = document.getElementById('home-pet-name');
  const homePetSubtext = document.getElementById('home-pet-subtext');
  const homePetAvatar = document.getElementById('home-pet-avatar');

  if (homePetName) homePetName.textContent = currentPet.name;
  if (homePetSubtext) homePetSubtext.textContent = `${currentPet.breed} • ${currentPet.age} • ${currentPet.weight}`;
  
  if (homePetAvatar) {
    if (currentPet.photoUrl) {
      homePetAvatar.innerHTML = `<img src="${currentPet.photoUrl}" class="w-full h-full object-cover">`;
    } else {
      homePetAvatar.textContent = currentPet.avatar || '🐕';
    }
  }

  // Update compatibility name
  const compatName = document.querySelector('#modal-compatibility span.text-xs.font-bold.mt-1.block');
  if (compatName) compatName.textContent = `우리 ${currentPet.name}`;
}

// Hook into DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  applyPetProfileToUI();
});
"""

if '// ================= 10. Dynamic Pet Profile Customizer' not in js:
    js = js + "\n" + pet_customizer_logic

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js updated with Pet Profile Customizer logic.")
