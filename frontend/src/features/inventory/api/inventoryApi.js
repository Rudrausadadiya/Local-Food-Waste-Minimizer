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

export const inventoryApi = {
  getBatches: (branchId, params) =>
    apiClient.get(`/inventory/batches/`, { params: { branch: branchId, ...params } }).then(unwrap),
  getBatch: (id) =>
    apiClient.get(`/inventory/batches/${id}/`).then((r) => r.data.data || r.data),
  getTransactions: (batchId) =>
    apiClient.get(`/inventory/transactions/`, { params: { batch: batchId } }).then(unwrap),
  adjustStock: (inventoryId, data) =>
    apiClient.post(`/inventory/inventories/${inventoryId}/stock_out/`, data).then((r) => r.data.data || r.data),
  createBatch: (data) => {
    const isFormData = data instanceof FormData;
    return apiClient.post('/inventory/batches/', data, isFormData ? { headers: { 'Content-Type': 'multipart/form-data' } } : {}).then((r) => r.data.data || r.data);
  },
  updateBatch: (id, data) =>
    apiClient.patch(`/inventory/batches/${id}/`, data).then((r) => r.data.data || r.data),
};
