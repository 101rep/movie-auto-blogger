/**
 * Core UI Helper (Toasts, Modals, Button Loading states)
 */
class UIHelper {
  showToast(message, type = 'info') {
    if (window.showToast) {
      window.showToast(message, type);
      return;
    }
    const color = type === 'success' ? 'bg-emerald-600' : (type === 'error' ? 'bg-rose-600' : 'bg-slate-800');
    const toast = document.createElement('div');
    toast.className = `fixed bottom-6 right-6 ${color} text-white px-4 py-2.5 rounded-xl shadow-xl text-xs font-bold z-50 transition transform translate-y-4 opacity-0`;
    toast.innerText = message;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.classList.remove('translate-y-4', 'opacity-0');
    }, 50);
    setTimeout(() => {
      toast.classList.add('opacity-0', 'translate-y-4');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  setLoading(btnId, isLoading, loadingText = '처리 중...') {
    const btn = typeof btnId === 'string' ? document.getElementById(btnId) : btnId;
    if (!btn) return;
    if (isLoading) {
      btn.dataset.prevHtml = btn.innerHTML;
      btn.disabled = true;
      btn.classList.add('opacity-75', 'cursor-not-allowed');
      btn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin mr-1.5"></i> ${loadingText}`;
    } else {
      btn.disabled = false;
      btn.classList.remove('opacity-75', 'cursor-not-allowed');
      if (btn.dataset.prevHtml) {
        btn.innerHTML = btn.dataset.prevHtml;
      }
    }
  }

  openModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) {
      el.classList.remove('hidden');
      el.classList.add('flex');
    }
  }

  closeModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) {
      el.classList.add('hidden');
      el.classList.remove('flex');
    }
  }
}

window.UI = new UIHelper();
