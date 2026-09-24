/**
 * Action Handlers for Content Management & Review
 */
class ContentActions {
  static async changeStatus(contentId, status) {
    try {
      await window.ContentService.updateStatus(contentId, status);
      window.UI.showToast(`상태가 [${status}]로 변경되었습니다!`, 'success');
      setTimeout(() => location.reload(), 500);
    } catch (e) {
      window.UI.showToast('상태 변경 실패: ' + e.message, 'error');
    }
  }

  static async assignAccount(contentId, accountId) {
    try {
      await window.ContentService.updateAccount(contentId, accountId);
      window.UI.showToast('발행 계정이 성공적으로 변경되었습니다!', 'success');
      setTimeout(() => location.reload(), 400);
    } catch (e) {
      window.UI.showToast('계정 변경 실패: ' + e.message, 'error');
    }
  }

  static async runAiReview(contentId) {
    const modal = document.getElementById('review-modal');
    const body = document.getElementById('review-modal-body');
    if (modal) {
      modal.classList.remove('hidden');
      modal.classList.add('flex');
    }
    if (body) {
      body.innerHTML = '<div class="py-6 text-center text-slate-400"><i class="fa-solid fa-spinner fa-spin text-lg mb-2"></i><p>AI 품질 및 공정위 정책 검수 중...</p></div>';
    }

    try {
      const data = await window.ContentService.runAiReview(contentId);
      const badgeClass = data.pass ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800';
      const badgeText = data.pass ? '검수 통과 (PASS)' : '수정 필요 (FLAGGED)';
      
      let issuesHtml = '';
      if (data.issues && data.issues.length > 0) {
        issuesHtml = '<div class="space-y-1"><strong class="text-rose-600">지적 사항:</strong><ul class="list-disc list-inside text-slate-600 space-y-0.5">' +
          data.issues.map(i => `<li>${i}</li>`).join('') + '</ul></div>';
      } else {
        issuesHtml = '<p class="text-emerald-600 font-semibold"><i class="fa-solid fa-circle-check"></i> 정책 위반 및 결함 없음</p>';
      }

      if (body) {
        body.innerHTML = `
          <div class="flex items-center justify-between bg-slate-50 p-3 rounded-xl border border-slate-200">
            <div>
              <span class="text-slate-500 font-semibold">종합 판정:</span>
              <span class="px-2 py-0.5 rounded-full font-bold text-xs ${badgeClass} ml-1">${badgeText}</span>
            </div>
            <div>
              <span class="text-slate-500 font-semibold">품질 점수:</span>
              <strong class="text-indigo-600 font-bold ml-1 text-sm">${data.quality_score}점</strong>
            </div>
          </div>
          <div class="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-2">
            <div class="flex justify-between text-slate-600">
              <span>공정위 표기 검수:</span>
              <strong class="${data.policy_passed ? 'text-emerald-600' : 'text-rose-600'}">${data.policy_passed ? '규정 준수' : '미준수'}</strong>
            </div>
            <div class="flex justify-between text-slate-600">
              <span>텍스트 유사도(중복률):</span>
              <strong class="text-slate-800">${(data.max_similarity * 100).toFixed(1)}%</strong>
            </div>
          </div>
          <div class="bg-indigo-50/50 p-3 rounded-xl border border-indigo-100">
            ${issuesHtml}
          </div>
          <div class="bg-slate-50 p-3 rounded-xl border border-slate-200">
            <strong class="text-slate-700 block mb-1">AI 피드백:</strong>
            <p class="text-slate-600 leading-relaxed">${data.feedback || '완벽한 형태의 콘텐츠입니다.'}</p>
          </div>
        `;
      }
    } catch (e) {
      if (body) body.innerHTML = `<div class="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl">검수 실패: ${e.message}</div>`;
    }
  }

  static openScheduleModal(contentId, title) {
    const idInput = document.getElementById('sched-content-id');
    const dtInput = document.getElementById('sched-datetime');
    if (idInput) idInput.value = contentId;
    if (dtInput) {
      const now = new Date();
      now.setHours(now.getHours() + 1);
      const localIso = new Date(now.getTime() - (now.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
      dtInput.value = localIso;
    }
    window.UI.openModal('schedule-modal');
  }

  static async submitSchedule(event) {
    if (event) event.preventDefault();
    const contentId = parseInt(document.getElementById('sched-content-id')?.value);
    const dt = document.getElementById('sched-datetime')?.value;

    try {
      await window.SchedulerService.schedule(contentId, new Date(dt).toISOString());
      window.UI.showToast('캘린더에 발행 일정이 예약되었습니다!', 'success');
      window.UI.closeModal('schedule-modal');
      setTimeout(() => location.href = '/calendar', 700);
    } catch (e) {
      window.UI.showToast('예약 실패: ' + e.message, 'error');
    }
  }

  static async publishNow(contentId) {
    if (!confirm('지금 즉시 Threads로 발행하시겠습니까?')) return;
    try {
      const data = await window.SchedulerService.publishNow(contentId);
      window.UI.showToast(`성공적으로 발행되었습니다! (ID: ${data.remote_post_id})`, 'success');
      setTimeout(() => location.href = '/calendar', 700);
    } catch (e) {
      window.UI.showToast('발행 실패: ' + e.message, 'error');
    }
  }

  static filterCluster(cluster) {
    document.querySelectorAll('.content-cluster-btn').forEach(b => {
      if (b.dataset.cluster === cluster) {
        b.className = 'content-cluster-btn px-3 py-1.5 rounded-lg bg-slate-900 text-white font-bold text-xs transition';
      } else {
        b.className = 'content-cluster-btn px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200 font-medium text-xs transition';
      }
    });

    const cards = document.querySelectorAll('.content-item-card');
    cards.forEach(card => {
      if (cluster === 'ALL' || card.dataset.cluster === cluster) {
        card.classList.remove('hidden');
      } else {
        card.classList.add('hidden');
      }
    });
  }
}

window.ContentActions = ContentActions;
