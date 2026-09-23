/**
 * Unified API Client with Cache & Error Interceptor
 */
class ApiClient {
  static async request(url, options = {}, useCache = false, cacheTtl = 60) {
    const method = options.method || 'GET';
    const cacheKey = `api:${method}:${url}:${JSON.stringify(options.body || '')}`;

    if (method === 'GET' && useCache) {
      const cached = window.AppCache.get(cacheKey);
      if (cached) return cached;
    }

    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, { ...options, headers });
      if (!response.ok) {
        let errDetail = `HTTP ${response.status}`;
        try {
          const errJson = await response.json();
          errDetail = errJson.detail || errJson.message || errDetail;
        } catch (_) {}
        throw new Error(errDetail);
      }
      const data = await response.json();

      if (method === 'GET' && useCache) {
        window.AppCache.set(cacheKey, data, cacheTtl);
      } else if (method !== 'GET') {
        // Invalidate related caches on mutating actions
        window.AppCache.invalidate('api:');
      }

      return data;
    } catch (err) {
      console.error(`[API Error] ${method} ${url}:`, err);
      throw err;
    }
  }

  static get(url, useCache = false, ttl = 60) {
    return this.request(url, { method: 'GET' }, useCache, ttl);
  }

  static post(url, data) {
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  static patch(url, data) {
    return this.request(url, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }

  static delete(url) {
    return this.request(url, { method: 'DELETE' });
  }
}

window.ApiClient = ApiClient;
