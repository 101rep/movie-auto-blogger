import os

app_file = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App\app.js"

with open(app_file, 'r', encoding='utf-8') as f:
    js = f.read()

tier_logic = """
// ================= 9. Free Trial & Membership Tier Access Gate =================
let guestUsage = JSON.parse(localStorage.getItem('petlog_guest_usage')) || {
  aiScan: 0,
  voice: 0,
  compat: 0,
  chartPdf: 0,
  chartLog: 0
};

window.checkFeatureAccess = function(featureKey, featureName) {
  // 1. If Logged-in Member (회원) -> 100% UNLIMITED FREE ACCESS!
  if (currentUser) {
    return true;
  }

  // 2. If Guest (비회원) -> Allow exactly 1 time free trial per feature
  const used = guestUsage[featureKey] || 0;
  if (used < 1) {
    guestUsage[featureKey] = used + 1;
    localStorage.setItem('petlog_guest_usage', JSON.stringify(guestUsage));
    // Toast notification
    showTrialToast(`🎁 [비회원 1회 무료 체험] '${featureName}'을(를) 무료 체험합니다. (1/1회 완료)`);
    return true;
  }

  // 3. If Guest already used the 1-time free trial -> Prompt Social Login Modal
  openTrialLimitModal(featureName);
  return false;
};

function showTrialToast(msg) {
  const toast = document.createElement('div');
  toast.className = 'fixed top-12 left-1/2 -translate-x-1/2 bg-neutral-900/90 text-white text-xs font-bold px-4 py-2.5 rounded-full shadow-2xl z-50 border border-amber-500/40 animate-bounce flex items-center gap-1.5 backdrop-blur-md';
  toast.innerHTML = `<span>✨</span><span>${msg}</span>`;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 3500);
}

window.openTrialLimitModal = function(featureName) {
  const modal = document.getElementById('modal-trial-limit');
  const titleEl = document.getElementById('limit-feature-name');
  if (titleEl) {
    titleEl.innerHTML = `'${featureName}' 비회원 1회 무료 체험이 종료되었습니다`;
  }
  if (modal) {
    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  }
};

window.closeTrialLimitModal = function() {
  const modal = document.getElementById('modal-trial-limit');
  if (modal) modal.classList.add('hidden');
};

// PRO Paid Services Modal Handlers
window.openProServiceModal = function(title, price, desc) {
  const modal = document.getElementById('modal-pro-service');
  if (modal) {
    const titleEl = document.getElementById('pro-modal-title');
    const priceEl = document.getElementById('pro-modal-price');
    const descEl = document.getElementById('pro-modal-desc');
    if (titleEl) titleEl.textContent = title;
    if (priceEl) priceEl.textContent = price;
    if (descEl) descEl.textContent = desc;
    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  }
};

window.closeProServiceModal = function() {
  const modal = document.getElementById('modal-pro-service');
  if (modal) modal.classList.add('hidden');
};

window.requestProServiceOrder = function() {
  if (!currentUser) {
    alert('전문가 1:1 매칭 및 예약 확인을 위해 먼저 간편 로그인을 진행해 주세요.');
    closeProServiceModal();
    openAuthModal();
    return;
  }
  alert(`👑 [${currentUser.name}]님, 전문가 1:1 예약 신청이 접수되었습니다!\\n담당 수의사/훈련사가 배정되는 즉시 카카오 알림톡으로 연락드립니다.`);
  closeProServiceModal();
};

// Update Tier Banner in Home
function updateTierBannerUI() {
  const banner = document.getElementById('membership-tier-banner');
  const title = document.getElementById('tier-badge-title');
  const desc = document.getElementById('tier-badge-desc');

  if (!banner) return;

  if (currentUser) {
    banner.className = 'bg-gradient-to-r from-emerald-500/10 via-indigo-500/10 to-teal-500/10 border border-emerald-500/30 rounded-2xl p-3 flex items-center justify-between cursor-pointer hover:border-emerald-500/50 transition-all';
    if (title) {
      title.className = 'text-xs font-black text-emerald-600 dark:text-emerald-400';
      title.innerHTML = `👑 [${currentUser.name}] 정회원 무제한 무료 패스 적용 중`;
    }
    if (desc) {
      desc.textContent = 'AI 사진 진단, 멍냥 궁합, 스마트 차트 PDF 평생 무제한 무료!';
    }
  } else {
    banner.className = 'bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-indigo-500/10 border border-amber-500/20 rounded-2xl p-3 flex items-center justify-between cursor-pointer hover:border-amber-500/40 transition-all';
    if (title) {
      title.className = 'text-xs font-black text-amber-600 dark:text-amber-400';
      title.textContent = '비회원 모든 기능 1회 무료 체험권 적용 중';
    }
    if (desc) {
      desc.textContent = '회원가입(1초) 시 유료 기능 외 모든 핵심 기능 무제한 무료!';
    }
  }
}
"""

# Modify triggerAIScan in app.js
old_trigger_ai = """window.triggerAIScan = function() {
  const dropzone = document.getElementById('ai-dropzone');"""
new_trigger_ai = """window.triggerAIScan = function() {
  if (!checkFeatureAccess('aiScan', 'AI 1초 사진 건강 스캐너')) return;
  const dropzone = document.getElementById('ai-dropzone');"""

js = js.replace(old_trigger_ai, new_trigger_ai)

# Modify simulateVoiceAnalysis
old_voice = """window.simulateVoiceAnalysis = function() {"""
new_voice = """window.simulateVoiceAnalysis = function() {
  if (!checkFeatureAccess('voice', '멍냥 음성 번역기')) return;"""

js = js.replace(old_voice, new_voice)

# Modify openCompatibilityModal
old_compat = """window.openCompatibilityModal = function() {"""
new_compat = """window.openCompatibilityModal = function() {
  if (!checkFeatureAccess('compat', '멍냥 궁합 & MBTI 분석기')) return;"""

js = js.replace(old_compat, new_compat)

# Modify exportDoctorChartPDF
old_pdf = """window.exportDoctorChartPDF = function() {"""
new_pdf = """window.exportDoctorChartPDF = function() {
  if (!checkFeatureAccess('chartPdf', '원장님 전송 PDF 차트 다운로드')) return;"""

js = js.replace(old_pdf, new_pdf)

# Modify saveHealthLog
old_save = """window.saveHealthLog = function() {"""
new_save = """window.saveHealthLog = function() {
  if (!checkFeatureAccess('chartLog', '스마트 닥터 차트 기록')) return;"""

js = js.replace(old_save, new_save)

# Hook updateTierBannerUI in applyUserLogin & logoutUser & DOMContentLoaded
if '// ================= 9. Free Trial' not in js:
    js = js + "\n" + tier_logic

js = js.replace('updateAuthUI();', 'updateAuthUI(); if (typeof updateTierBannerUI === "function") updateTierBannerUI();')

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js updated with Tier Policy & Free Trial Gate successfully.")
