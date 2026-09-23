/**
 * Action Handlers for Product Detail Pipeline
 */
class ProductActions {
  static async runScoring(productId) {
    const btn = document.getElementById('btn-score');
    window.UI.setLoading(btn, true, '채점 중...');
    try {
      await window.ProductService.score(productId);
      window.UI.showToast('상품 6대 지표 점수화 완료!', 'success');
      setTimeout(() => location.reload(), 500);
    } catch (e) {
      window.UI.showToast('점수화 실패: ' + e.message, 'error');
      window.UI.setLoading(btn, false);
    }
  }

  static async runDNA(productId, forceRefresh = false) {
    const btn = forceRefresh ? document.getElementById('btn-dna-refresh') : document.getElementById('btn-dna');
    window.UI.setLoading(btn, true, '분석 중...');
    try {
      await window.ProductService.generateDNA(productId, forceRefresh);
      window.UI.showToast('상품 DNA 생성 완료!', 'success');
      setTimeout(() => location.reload(), 500);
    } catch (e) {
      window.UI.showToast('DNA 분석 실패: ' + e.message, 'error');
      window.UI.setLoading(btn, false);
    }
  }

  static async runIdeas(productId) {
    const btn = document.getElementById('btn-ideas');
    window.UI.setLoading(btn, true, '10개 생성 중...');
    try {
      const data = await window.ProductService.generateIdeas(productId);
      window.UI.showToast(`10대 각도 아이디어 ${data.count || 10}개 생성 완료!`, 'success');
      setTimeout(() => location.reload(), 500);
    } catch (e) {
      window.UI.showToast('아이디어 생성 실패: ' + e.message, 'error');
      window.UI.setLoading(btn, false);
    }
  }

  static async updateIdeaStatus(ideaId, status) {
    try {
      await window.ProductService.updateIdeaStatus(ideaId, status);
      window.UI.showToast('아이디어 상태가 변경되었습니다.', 'success');
    } catch (e) {
      window.UI.showToast('상태 변경 실패: ' + e.message, 'error');
    }
  }

  static async openWriterModal(productId, ideaId, hook) {
    window.AppState.set('writer_product_id', productId);
    window.AppState.set('writer_idea_id', ideaId);
    window.UI.openModal('writer-modal');
    await this.generateDraft('default');
  }

  static closeWriterModal() {
    window.UI.closeModal('writer-modal');
  }

  static async generateDraft(mode) {
    document.querySelectorAll('.rewrite-btn').forEach(b => {
      if (b.dataset.mode === mode) {
        b.className = 'rewrite-btn bg-slate-900 text-white px-3 py-1.5 rounded-lg font-semibold transition';
      } else {
        b.className = 'rewrite-btn bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg font-medium transition';
      }
    });

    const bodyEl = document.getElementById('modal-post-body');
    if (bodyEl) bodyEl.value = 'Threads 본문을 작성하는 중입니다...';

    const productId = window.AppState.get('writer_product_id');
    const ideaId = window.AppState.get('writer_idea_id');

    try {
      const postData = await window.ProductService.writeThreadsPost(productId, ideaId, mode);
      if (bodyEl) bodyEl.value = postData.body;

      const commData = await window.ProductService.generateComments(productId);
      window.AppState.set('writer_comments', commData.comments || []);
      this.renderComments(commData.comments || []);
    } catch (e) {
      if (bodyEl) bodyEl.value = '오류: ' + e.message;
      window.UI.showToast('작성 오류: ' + e.message, 'error');
    }
  }

  static renderComments(comments) {
    const container = document.getElementById('modal-comments-container');
    if (!container) return;
    container.innerHTML = comments.map((c, i) => `
      <div class="bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-1.5">
        <div class="flex items-center justify-between text-[11px] font-bold text-slate-600">
          <span>댓글 ${c.sequence}</span>
          <span class="text-slate-400 font-normal">개별 수정 가능</span>
        </div>
        <textarea id="comment-text-${i}" rows="2" class="w-full bg-white border border-slate-200 rounded-lg p-2 text-xs text-slate-800 focus:outline-none focus:border-brand-500">${c.body}</textarea>
      </div>
    `).join('');
  }

  static async saveFinalContent(status) {
    const body = document.getElementById('modal-post-body')?.value.trim();
    if (!body) {
      window.UI.showToast('본문 내용이 비어있습니다.', 'error');
      return;
    }

    const currentComments = window.AppState.get('writer_comments', []);
    const commentsToSave = currentComments.map((c, i) => {
      const textarea = document.getElementById(`comment-text-${i}`);
      return {
        sequence: c.sequence,
        body: textarea ? textarea.value.trim() : c.body,
        link: c.link,
        status: 'ACTIVE'
      };
    });

    const productId = window.AppState.get('writer_product_id');
    const ideaId = window.AppState.get('writer_idea_id');
    const accountSelect = document.getElementById('writer-account-select');
    const accountId = accountSelect && accountSelect.value ? parseInt(accountSelect.value) : null;

    try {
      const payload = {
        product_id: productId,
        idea_id: ideaId,
        account_id: accountId,
        title: document.title.split(' - ')[0] || '큐레이션 글',
        body: body,
        status: status,
        comments: commentsToSave
      };
      await window.ContentService.saveContent(payload);
      window.UI.showToast(`콘텐츠가 [${status}] 상태로 저장되었습니다!`, 'success');
      this.closeWriterModal();
      setTimeout(() => location.href = '/content', 500);
    } catch (e) {
      window.UI.showToast('저장 실패: ' + e.message, 'error');
    }
  }

  static async runAllWorkflow(productId) {
    const btn = document.getElementById('btn-run-all');
    window.UI.setLoading(btn, true, '전자동 완성 중...');
    try {
      await window.ProductService.score(productId);
      await window.ProductService.generateDNA(productId);
      await window.ProductService.generateIdeas(productId);
      window.UI.showToast('점수 + DNA + 10대 아이디어 전자동 완성 완료!', 'success');
      setTimeout(() => location.reload(), 500);
    } catch (e) {
      window.UI.showToast('완성 실패: ' + e.message, 'error');
      window.UI.setLoading(btn, false);
    }
  }

  static async deleteProduct(productId) {
    if (!confirm('정말 이 상품을 삭제하시겠습니까? 연결된 점수, DNA, 아이디어가 함께 삭제됩니다.')) return;
    try {
      await window.ProductService.deleteProduct(productId);
      window.UI.showToast('상품이 삭제되었습니다.', 'success');
      setTimeout(() => location.href = '/products', 500);
    } catch (e) {
      window.UI.showToast('삭제 실패: ' + e.message, 'error');
    }
  }
}

window.ProductActions = ProductActions;
