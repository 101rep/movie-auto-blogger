/**
 * Content Feature Service
 */
class ContentService {
  static async updateStatus(contentId, status) {
    return window.ApiClient.patch(`/api/workflow/content/${contentId}/status`, { status });
  }

  static async updateAccount(contentId, accountId) {
    return window.ApiClient.patch(`/api/workflow/content/${contentId}/account`, { account_id: accountId });
  }

  static async runAiReview(contentId) {
    return window.ApiClient.get(`/api/review/${contentId}`);
  }

  static async saveBody(contentId, body) {
    // In-line body update
    return window.ApiClient.patch(`/api/workflow/content/${contentId}/body`, { body });
  }

  static async saveContent(payload) {
    return window.ApiClient.post('/api/workflow/content/save', payload);
  }
}

window.ContentService = ContentService;
