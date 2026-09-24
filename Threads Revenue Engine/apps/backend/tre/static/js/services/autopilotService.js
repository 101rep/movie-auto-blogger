/**
 * Autopilot & Golden Pick Feature Service
 */
class AutopilotService {
  static async runAutopilot({ keyword, hoursLater = 2, accountId = null }) {
    return window.ApiClient.post('/api/autopilot/run', {
      keyword,
      hours_later: hoursLater,
      account_id: accountId
    });
  }

  static async runGoldenPick({ minScore = 90, accountId = null } = {}) {
    return window.ApiClient.post('/api/autopilot/golden-pick', {
      min_score: minScore,
      account_id: accountId
    });
  }

  static async runBulk({ keywords, intervalHours = 3 }) {
    return window.ApiClient.post('/api/bulk/process', {
      keywords,
      interval_hours: intervalHours
    });
  }
}

window.AutopilotService = AutopilotService;
