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

export const donationsApi = {
  getNgos: (params) => apiClient.get('/donations/ngos/', { params }).then(unwrap),
  getNgoById: (id) => apiClient.get(`/donations/ngos/${id}/`).then((r) => r.data.data || r.data),
  verifyNgo: (id) => apiClient.post(`/donations/ngos/${id}/verify/`).then((r) => r.data.data || r.data),

  getDonationListings: (params) => apiClient.get('/donations/listings/', { params }).then(unwrap),
  createDonationListing: (data) => apiClient.post('/donations/listings/', data).then((r) => r.data.data || r.data),
  convertFromMarketplace: (marketplaceListingId) =>
    apiClient.post('/donations/listings/convert_marketplace/', { marketplace_listing_id: marketplaceListingId }).then((r) => r.data.data || r.data),

  getDonationRequests: (params) => apiClient.get('/donations/requests/', { params }).then(unwrap),
  createDonationRequest: (data) => apiClient.post('/donations/requests/', data).then((r) => r.data.data || r.data),
  approveDonationRequest: (id, approvedQuantity) =>
    apiClient.post(`/donations/requests/${id}/approve/`, { approved_quantity: approvedQuantity }).then((r) => r.data.data || r.data),

  getDonationPickups: (params) => apiClient.get('/donations/pickups/', { params }).then(unwrap),
  completePickup: (id, data) => apiClient.post(`/donations/pickups/${id}/complete_pickup/`, data).then((r) => r.data.data || r.data),

  getImpactSummary: () => apiClient.get('/donations/impact/summary/').then((r) => r.data.data || r.data),
  getImpacts: (params) => apiClient.get('/donations/impacts/', { params }).then(unwrap),

  getPickupRoutes: (params) => apiClient.get('/donations/routes/', { params }).then(unwrap),
  createPickupRoute: (data) => apiClient.post('/donations/routes/', data).then((r) => r.data.data || r.data),
};
