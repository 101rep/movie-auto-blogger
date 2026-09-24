/**
 * Action Handlers for Autopilot, Golden Pick, and Bulk
 * Completely isolates UI button clicks from business logic & API calls!
 */
class AutopilotActions {
  static async loadAccountDropdown(selectElementId, defaultText = '🤖 AI 스마트 자동 매칭 (상품 맞춤 계정 배정)') {
    const sel = document.getElementById(selectElementId);
    if (!sel) return;
    try {
      const accounts = await window.AccountService.getAccounts(true);
      sel.innerHTML = `<option value="">${defaultText}</option>`;
      accounts.forEach(acc => {
        const clusterLabel = acc.cluster_type === 'VERTICAL' ? '[버티컬]' : (acc.cluster_type === 'PERSONA' ? '[페르소나]' : '[트렌드]');
        sel.innerHTML += `<option value="${acc.id}">${clusterLabel} @${acc.username} (${acc.display_name})</option>`;
      });
    } catch (e) {
      console.warn('Account dropdown load warning:', e);
    }
  }

  // --- 1. Autopilot Modal ---
  static openAutopilotModal() {
    window.UI.openModal('autopilot-modal');
    document.getElementById('autopilot-form-section')?.classList.remove('hidden');
    document.getElementById('autopilot-progress-section')?.classList.add('hidden');
    document.getElementById('autopilot-result-section')?.classList.add('hidden');
    this.loadAccountDropdown('auto-account-select');
  }

  static closeAutopilotModal() {
    window.UI.closeModal('autopilot-modal');
  }

  static async submitAutopilot() {
    const keywordInput = document.getElementById('auto-keyword');
    const hoursInput = document.getElementById('auto-hours');
    const accInput = document.getElementById('auto-account-select');

    const keyword = keywordInput ? keywordInput.value.trim() : '';
    const hours = hoursInput ? parseInt(hoursInput.value) : 2;
    const accountId = accInput && accInput.value ? parseInt(accInput.value) : null;

    if (!keyword) {
      window.UI.showToast('상품 탐색 키워드를 입력해주세요!', 'error');
      return;
    }

    document.getElementById('autopilot-form-section')?.classList.add('hidden');
    document.getElementById('autopilot-progress-section')?.classList.remove('hidden');
    const stepsBox = document.getElementById('auto-steps-box');
    if (stepsBox) stepsBox.innerHTML = '<div class="text-slate-500"><i class="fa-solid fa-spinner fa-spin mr-1.5"></i> 파이프라인 가동 중...</div>';

    try {
      const data = await window.AutopilotService.runAutopilot({ keyword, hoursLater: hours, accountId });
      
      if (stepsBox) {
        stepsBox.innerHTML = (data.steps || []).map(s => 
          `<div class="flex items-center gap-2 text-slate-700 py-1 border-b border-slate-100 last:border-0"><i class="fa-solid fa-check text-emerald-500"></i> ${s}</div>`
        ).join('');
      }

      const accInfo = data.account ? `@${data.account.username} (${data.account.display_name})` : 'AI 자동 매칭 계정';
      const summaryEl = document.getElementById('auto-result-summary');
      if (summaryEl) {
        summaryEl.innerHTML = `
          <strong>상품:</strong> ${data.product_name}<br>
          <strong>발행 계정:</strong> <span class="font-bold text-indigo-700">${accInfo}</span><br>
          <strong>글 제목:</strong> ${data.title}<br>
          <strong>예약 일시:</strong> ${new Date(data.scheduled_at).toLocaleString()}
        `;
      }

      setTimeout(() => {
        document.getElementById('autopilot-progress-section')?.classList.add('hidden');
        document.getElementById('autopilot-result-section')?.classList.remove('hidden');
        window.UI.showToast('오토파일럿 파이프라인이 성공적으로 완료되었습니다!', 'success');
      }, 700);

    } catch (e) {
      if (stepsBox) stepsBox.innerHTML = `<div class="p-3 bg-rose-50 text-rose-700 rounded-xl font-bold">실행 실패: ${e.message}</div>`;
      window.UI.showToast('오토파일럿 실패: ' + e.message, 'error');
    }
  }

  // --- 2. Golden Pick 90+ ---
  static openGoldenPickModal() {
    window.UI.openModal('golden-pick-modal');
    this.loadAccountDropdown('golden-account-select');
  }

  static closeGoldenPickModal() {
    window.UI.closeModal('golden-pick-modal');
  }

  static async submitGoldenPick() {
    const accInput = document.getElementById('golden-account-select');
    const accountId = accInput && accInput.value ? parseInt(accInput.value) : null;

    const statusText = document.getElementById('golden-status-text');
    const stepsBox = document.getElementById('golden-steps-box');
    const progressSection = document.getElementById('golden-progress-section');
    const resultSection = document.getElementById('golden-result-section');
    const setupSection = document.getElementById('golden-setup-section');

    if (setupSection) setupSection.classList.add('hidden');
    if (progressSection) progressSection.classList.remove('hidden');
    if (resultSection) resultSection.classList.add('hidden');

    if (stepsBox) stepsBox.innerHTML = '<div class="text-amber-700 font-bold"><i class="fa-solid fa-spinner fa-spin mr-1.5"></i> 화제성 후보군 탐색 및 6대 지표 채점 중...</div>';

    try {
      const data = await window.AutopilotService.runGoldenPick({ minScore: 90, accountId });

      if (stepsBox) {
        stepsBox.innerHTML = (data.steps || []).map(s => 
          `<div class="flex items-center gap-2 text-slate-700 py-1 border-b border-slate-100 last:border-0"><i class="fa-solid fa-crown text-amber-500"></i> ${s}</div>`
        ).join('');
      }

      if (statusText) statusText.innerText = `👑 90점 돌파 골든 픽 발굴 및 예약 완료! (${data.score}점)`;

      const winnerImg = document.getElementById('golden-winner-img');
      if (winnerImg) winnerImg.src = data.product_image || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80';
      
      const titleEl = document.getElementById('golden-winner-title');
      if (titleEl) titleEl.innerText = data.product_name;

      const scoreEl = document.getElementById('golden-winner-score');
      if (scoreEl) scoreEl.innerText = `${data.score}점`;

      const priceEl = document.getElementById('golden-winner-price');
      if (priceEl) priceEl.innerText = `${Number(data.product_price).toLocaleString()}원`;

      const reasonEl = document.getElementById('golden-winner-reason');
      if (reasonEl) reasonEl.innerText = data.reason || '전환율, 바이럴 잠재력, 가격대 마진 90점 이상 획득';

      const postTitleEl = document.getElementById('golden-post-title');
      if (postTitleEl) postTitleEl.innerText = data.title;

      const postBodyEl = document.getElementById('golden-post-body');
      if (postBodyEl) postBodyEl.innerText = data.body;

      const timeEl = document.getElementById('golden-scheduled-time');
      if (timeEl) timeEl.innerText = new Date(data.scheduled_at).toLocaleString();

      const accBadgeEl = document.getElementById('golden-target-acc-badge');
      if (accBadgeEl && data.account) {
        const clusterText = data.account.cluster_type === 'VERTICAL' ? '버티컬 전문' : (data.account.cluster_type === 'PERSONA' ? '타깃 페르소나' : '트렌드/이슈');
        accBadgeEl.innerHTML = `<span class="bg-indigo-100 text-indigo-800 text-[10px] font-black px-2 py-0.5 rounded-full mr-1">${clusterText}</span> @${data.account.username} (${data.account.display_name})`;
      }

      setTimeout(() => {
        if (progressSection) progressSection.classList.add('hidden');
        if (resultSection) resultSection.classList.remove('hidden');
        window.UI.showToast('오늘의 90점+ AI 골든 픽이 캘린더에 성공적으로 예약되었습니다!', 'success');
      }, 700);

    } catch (e) {
      if (stepsBox) stepsBox.innerHTML = `<div class="p-3 bg-rose-50 text-rose-700 rounded-xl font-bold">골든 픽 실행 실패: ${e.message}</div>`;
      if (statusText) statusText.innerText = '오류 발생';
      window.UI.showToast('골든 픽 실패: ' + e.message, 'error');
    }
  }

  // --- 3. Bulk Modal ---
  static openBulkModal() {
    window.UI.openModal('bulk-modal');
    document.getElementById('bulk-form-section')?.classList.remove('hidden');
    document.getElementById('bulk-progress-section')?.classList.add('hidden');
    document.getElementById('bulk-result-section')?.classList.add('hidden');
  }

  static closeBulkModal() {
    window.UI.closeModal('bulk-modal');
  }

  static async submitBulk() {
    const rawText = document.getElementById('bulk-keywords')?.value.trim();
    const interval = parseInt(document.getElementById('bulk-interval')?.value || '3');

    if (!rawText) {
      window.UI.showToast('최소 1개 이상의 키워드를 입력해주세요!', 'error');
      return;
    }

    const keywords = rawText.split('\n').map(k => k.trim()).filter(k => k.length > 0);
    if (keywords.length === 0) {
      window.UI.showToast('유효한 키워드를 입력해주세요!', 'error');
      return;
    }

    document.getElementById('bulk-form-section')?.classList.add('hidden');
    document.getElementById('bulk-progress-section')?.classList.remove('hidden');
    const stepsBox = document.getElementById('bulk-steps-box');
    if (stepsBox) stepsBox.innerHTML = `<div class="text-indigo-600"><i class="fa-solid fa-spinner fa-spin mr-1.5"></i> 총 ${keywords.length}개 키워드 순차 배치 가동 중...</div>`;

    try {
      const data = await window.AutopilotService.runBulk({ keywords, intervalHours: interval });

      if (stepsBox) {
        stepsBox.innerHTML = (data.results || []).map(r => 
          `<div class="flex items-center justify-between text-slate-700 py-1.5 border-b border-slate-100 last:border-0">
            <span><i class="fa-solid fa-circle-check text-emerald-500 mr-1"></i> [${r.keyword}] ${(r.title || '').substring(0, 20)}...</span>
            <span class="text-[10px] text-indigo-600 font-bold">${new Date(r.scheduled_at).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>
          </div>`
        ).join('');
      }

      const summaryEl = document.getElementById('bulk-result-summary');
      if (summaryEl) {
        summaryEl.innerHTML = `
          <strong>총 처리 건수:</strong> ${data.total_processed}건 중 <strong>${data.success_count}건 성공</strong> 완료!<br>
          캘린더에 ${interval}시간 간격으로 모든 발행 일정이 배치되었습니다.
        `;
      }

      setTimeout(() => {
        document.getElementById('bulk-progress-section')?.classList.add('hidden');
        document.getElementById('bulk-result-section')?.classList.remove('hidden');
        window.UI.showToast('대량 벌크 캘린더 배치가 완료되었습니다!', 'success');
      }, 700);

    } catch (e) {
      if (stepsBox) stepsBox.innerHTML = `<div class="p-3 bg-rose-50 text-rose-700 rounded-xl font-bold">벌크 처리 실패: ${e.message}</div>`;
      window.UI.showToast('벌크 처리 오류: ' + e.message, 'error');
    }
  }
}

window.AutopilotActions = AutopilotActions;
window.openAutopilotModal = () => AutopilotActions.openAutopilotModal();
window.closeAutopilotModal = () => AutopilotActions.closeAutopilotModal();
window.runAutopilot = () => AutopilotActions.submitAutopilot();
window.openBulkModal = () => AutopilotActions.openBulkModal();
window.closeBulkModal = () => AutopilotActions.closeBulkModal();
window.runBulkAutopilot = () => AutopilotActions.submitBulk();
window.openGoldenPickModal = () => AutopilotActions.openGoldenPickModal();
window.closeGoldenPickModal = () => AutopilotActions.closeGoldenPickModal();
window.runGoldenPickAutopilot = () => AutopilotActions.openGoldenPickModal();
window.loadAccountsDropdown = () => AutopilotActions.loadAccountDropdown('auto-account-select');
