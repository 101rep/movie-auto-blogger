/**
 * Action Handlers for Settings & Account Management
 */
class SettingsActions {
  static filterCluster(cluster) {
    document.querySelectorAll('.acc-filter-btn').forEach(btn => {
      if (btn.id === `af-${cluster}`) {
        btn.className = 'acc-filter-btn px-3 py-1.5 rounded-lg bg-slate-900 text-white';
      } else {
        btn.className = 'acc-filter-btn px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200';
      }
    });

    const cards = document.querySelectorAll('.account-card');
    cards.forEach(card => {
      const cType = card.dataset.cluster;
      if (cluster === 'ALL' || cType === cluster) {
        card.classList.remove('hidden');
      } else {
        card.classList.add('hidden');
      }
    });
  }

  static async submitNewAccount(event) {
    if (event) event.preventDefault();
    const payload = {
      cluster_type: document.getElementById('acc-cluster')?.value || 'VERTICAL',
      display_name: document.getElementById('acc-name')?.value.trim() || '',
      username: document.getElementById('acc-handle')?.value.trim().replace(/^@/, '') || '',
      category: document.getElementById('acc-category')?.value.trim() || '전체',
      target_audience: document.getElementById('acc-target')?.value.trim() || '',
      tone: document.getElementById('acc-tone')?.value || '친근하고 진솔한 일상 어조',
      access_token: document.getElementById('acc-token')?.value.trim() || null
    };

    try {
      await window.AccountService.createAccount(payload);
      window.UI.showToast('신규 계정이 성공적으로 등록되었습니다!', 'success');
      setTimeout(() => location.reload(), 500);
    } catch (e) {
      window.UI.showToast('계정 등록 실패: ' + e.message, 'error');
    }
  }

  static async deleteAccount(accountId, username) {
    if (!confirm(`정말 @${username} 계정을 삭제하시겠습니까?`)) return;
    try {
      await window.AccountService.deleteAccount(accountId);
      window.UI.showToast('계정이 삭제되었습니다.', 'success');
      setTimeout(() => location.reload(), 500);
    } catch (e) {
      window.UI.showToast('삭제 실패: ' + e.message, 'error');
    }
  }
}

window.SettingsActions = SettingsActions;
