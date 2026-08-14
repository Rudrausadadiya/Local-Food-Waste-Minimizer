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

export const businessApi = {
  getMyBusiness: () =>
    apiClient.get('/business/businesses/').then(unwrap),
  getBusiness: (id) =>
    apiClient.get(`/business/businesses/${id}/`).then((r) => r.data.data || r.data),
  createBusiness: (data) =>
    apiClient.post('/business/businesses/', data).then((r) => r.data.data || r.data),
  updateBusiness: (id, data) =>
    apiClient.patch(`/business/businesses/${id}/`, data).then((r) => r.data.data || r.data),
  getBranches: (businessId) =>
    apiClient.get('/business/branches/', { params: { business_id: businessId } }).then(unwrap),
  createBranch: (businessId, data) =>
    apiClient.post('/business/branches/', { business: businessId, ...data }).then((r) => r.data.data || r.data),
  updateBranch: (businessId, branchId, data) =>
    apiClient.patch(`/business/branches/${branchId}/`, data).then((r) => r.data.data || r.data),
  // Admin endpoints
  getAllBusinesses: (params) =>
    apiClient.get('/business/businesses/', { params }).then(unwrap),
  approveBusiness: (id) =>
    apiClient.post(`/business/businesses/${id}/verify/`).then((r) => r.data.data || r.data),
  rejectBusiness: (id, reason) =>
    apiClient.patch(`/business/businesses/${id}/`, { business_status: 'REJECTED' }).then((r) => r.data.data || r.data),
  toggleVerifyBusiness: (id, isVerified) =>
    apiClient.patch(`/business/businesses/${id}/`, { is_verified: isVerified }).then((r) => r.data.data || r.data),
  updateBusinessStatus: (id, status) =>
    apiClient.patch(`/business/businesses/${id}/`, { business_status: status }).then((r) => r.data.data || r.data),
  deleteBusiness: (id) =>
    apiClient.delete(`/business/businesses/${id}/`),
};
