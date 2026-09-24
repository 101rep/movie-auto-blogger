/**
 * Account Feature Service
 */
class AccountService {
  static async getAccounts(useCache = true) {
    return window.ApiClient.get('/api/accounts', useCache, 120);
  }

  static async createAccount(data) {
    const res = await window.ApiClient.post('/api/accounts', data);
    window.AppCache.invalidate('api:GET:/api/accounts');
    return res;
  }

  static async deleteAccount(id) {
    const res = await window.ApiClient.delete(`/api/accounts/${id}`);
    window.AppCache.invalidate('api:GET:/api/accounts');
    return res;
  }
}

window.AccountService = AccountService;
