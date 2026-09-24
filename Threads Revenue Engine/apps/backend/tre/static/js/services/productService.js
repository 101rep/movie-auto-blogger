/**
 * Product Feature Service
 */
class ProductService {
  static async search(query = '', category = '전체', limit = 50) {
    return window.ApiClient.get(`/api/products/search?query=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}&limit=${limit}`, true, 60);
  }

  static async score(productId) {
    return window.ApiClient.post(`/api/workflow/score/${productId}`, {});
  }

  static async generateDNA(productId, forceRefresh = false) {
    return window.ApiClient.post(`/api/workflow/dna/${productId}?force_refresh=${forceRefresh}`, {});
  }

  static async generateIdeas(productId) {
    return window.ApiClient.post(`/api/workflow/ideas/${productId}`, {});
  }

  static async updateIdeaStatus(ideaId, status) {
    return window.ApiClient.patch(`/api/workflow/ideas/${ideaId}/status`, { status });
  }

  static async writeThreadsPost(productId, ideaId, rewriteMode = 'default') {
    return window.ApiClient.post('/api/workflow/threads/write', {
      product_id: productId,
      idea_id: ideaId,
      rewrite_mode: rewriteMode
    });
  }

  static async generateComments(productId) {
    return window.ApiClient.post('/api/workflow/comments/generate', {
      product_id: productId
    });
  }

  static async deleteProduct(productId) {
    return window.ApiClient.delete(`/api/products/${productId}`);
  }
}

window.ProductService = ProductService;
