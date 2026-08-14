import { apiClient } from '../../../api/client';

// Function: unwrap
const unwrap = (res) => {
  const d = res.data;
  if (Array.isArray(d)) return d;
  if (Array.isArray(d?.data?.results)) return d.data.results;
  if (Array.isArray(d?.data)) return d.data;
  if (Array.isArray(d?.results)) return d.results;
  return [];
};

export const notificationsApi = {
  getNotifications: (params) => apiClient.get('/notifications/inbox/', { params }).then(unwrap),
  markAsRead: (id) => apiClient.post(`/notifications/inbox/${id}/mark_as_read/`).then((r) => r.data.data || r.data),
  markAllAsRead: () => apiClient.post('/notifications/inbox/mark_all_as_read/').then((r) => r.data.data || r.data),
  getPreferences: () => apiClient.get('/notifications/preferences/me/').then((r) => r.data.data || r.data),
  updatePreferences: (data) => apiClient.patch('/notifications/preferences/update_me/', data).then((r) => r.data.data || r.data),
};
