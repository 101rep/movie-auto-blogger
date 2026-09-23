/**
 * Scheduler Feature Service
 */
class SchedulerService {
  static async schedule(contentId, scheduledAt) {
    return window.ApiClient.post('/api/scheduler/schedule', {
      content_id: contentId,
      scheduled_at: scheduledAt
    });
  }

  static async publishNow(contentId) {
    return window.ApiClient.post(`/api/scheduler/publish-now/${contentId}`, {});
  }

  static async cancel(contentId) {
    return window.ApiClient.post(`/api/scheduler/cancel/${contentId}`, {});
  }
}

window.SchedulerService = SchedulerService;
