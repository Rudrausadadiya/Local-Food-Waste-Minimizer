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

export const ordersApi = {
  getVendorOrders: (params) =>
    apiClient.get('/marketplace/orders/', { params }).then(unwrap),
  getCustomerOrders: (params) =>
    apiClient.get('/marketplace/orders/', { params }).then(unwrap),
  verifyClaimCode: (code) =>
    apiClient.post('/marketplace/orders/verify_claim_code/', { claim_code: code }).then((r) => r.data.data || r.data),
  completeOrder: (id) =>
    apiClient.post(`/marketplace/orders/${id}/complete/`)
      .catch(() => apiClient.post(`/orders/orders/${id}/complete/`))
      .then((r) => r.data.data || r.data),
  cancelOrder: (id) =>
    apiClient.post(`/marketplace/orders/${id}/cancel/`)
      .catch(() => apiClient.post(`/orders/orders/${id}/cancel/`))
      .then((r) => r.data.data || r.data),
  dispatchDelivery: (id) =>
    apiClient.post(`/orders/orders/${id}/dispatch_delivery/`).then((r) => r.data.data || r.data),
  markDelivered: (id) =>
    apiClient.post(`/orders/orders/${id}/mark_delivered/`).then((r) => r.data.data || r.data),
  getCustomerLoyalty: (customerId) =>
    apiClient.get(`/orders/customers/${customerId}/loyalty/`).then((r) => r.data.data || r.data),
  createOrder: (listingId, quantity = 1, redeemPoints = 0, userLat = null, userLon = null) => {
    const payload = typeof listingId === 'object'
      ? { ...listingId, redeem_points: redeemPoints }
      : { listing: listingId, quantity, redeem_points: redeemPoints, user_lat: userLat, user_lon: userLon };
    return apiClient.post('/marketplace/orders/', payload).then((r) => r.data.data || r.data);
  },
};
