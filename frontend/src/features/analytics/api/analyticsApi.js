import { apiClient } from '../../../api/client';

export const analyticsApi = {
  getDashboardSummary: (params) =>
    apiClient.get('/analytics/dashboard/', { params }).then((r) => r.data.data || r.data),
  
  getDataQuality: (params) =>
    apiClient.get('/analytics/dashboard/data_quality/', { params }).then((r) => r.data.data || r.data),
  
  downloadReport: (params) =>
    apiClient.get('/analytics/reports/download/', { params, responseType: 'blob' }).then((r) => r.data),
  
  getScheduledReports: () =>
    apiClient.get('/analytics/schedules/').then((r) => r.data.results || r.data.data || r.data),
};
