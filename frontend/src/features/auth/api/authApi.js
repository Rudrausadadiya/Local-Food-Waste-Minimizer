import { apiClient } from '../../../api/client';

export const authApi = {
  login: async (credentials) => {
    const r = await apiClient.post('/users/auth/login/', credentials);
    const payload = r.data.data || r.data;
    return {
      user: payload.user,
      access: payload.tokens?.access || payload.access,
      refresh: payload.tokens?.refresh || payload.refresh,
    };
  },
  register: async (userData) => {
    const r = await apiClient.post('/users/auth/register/', userData);
    return r.data.data || r.data;
  },
  logout: (refresh) =>
    apiClient.post('/users/auth/logout/', { refresh }),
  getProfile: async () => {
    const r = await apiClient.get('/users/profile/');
    return r.data.data || r.data;
  },
  updateProfile: async (data) => {
    const r = await apiClient.patch('/users/profile/', data);
    return r.data.data || r.data;
  },
  forgotPassword: (email) =>
    apiClient.post('/users/auth/forgot-password/', { email }),
  resetPassword: (data) =>
    apiClient.post('/users/auth/reset-password/', data),
  verifyEmail: (data) =>
    apiClient.post('/users/auth/verify-email/', data),
  deactivateAccount: () =>
    apiClient.delete('/users/profile/'),
  getAdminUsers: async (params) => {
    const r = await apiClient.get('/users/admin/users/', { params });
    const d = r.data;
    if (Array.isArray(d)) return d;
    if (Array.isArray(d?.data)) return d.data;
    if (Array.isArray(d?.results)) return d.results;
    return [];
  },
  toggleUserStatus: async (userId, isActive) => {
    const r = await apiClient.post(`/users/admin/users/${userId}/toggle/`, { is_active: isActive });
    return r.data.data || r.data;
  },
};
