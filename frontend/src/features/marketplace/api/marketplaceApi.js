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

export const marketplaceApi = {
  getPublicListings: (params) =>
    apiClient.get('/marketplace/listings/', { params }).then(unwrap),
  getAllListingsAdmin: () =>
    apiClient.get('/marketplace/listings/', { params: { admin: 'true' } }).then(unwrap),
  getListing: (id) =>
    apiClient.get(`/marketplace/listings/${id}/`).then((r) => r.data.data || r.data),
  getMyListings: (params) =>
    apiClient.get('/marketplace/listings/', { params }).then(unwrap),
  createListing: (data) =>
    apiClient.post('/marketplace/listings/', data).then((r) => r.data.data || r.data),
  updateListing: (id, data) =>
    apiClient.patch(`/marketplace/listings/${id}/`, data).then((r) => r.data.data || r.data),
  takedownListing: (id, reason = '') =>
    apiClient.post(`/marketplace/listings/${id}/takedown/`, { reason }).then((r) => r.data.data || r.data),
  republishListing: (id) =>
    apiClient.post(`/marketplace/listings/${id}/republish/`).then((r) => r.data.data || r.data),
  deleteListing: (id) =>
    apiClient.delete(`/marketplace/listings/${id}/`),
  addToWishlist: (id) =>
    apiClient.post(`/marketplace/listings/${id}/add_to_wishlist/`),
  removeFromWishlist: (id) =>
    apiClient.delete(`/marketplace/wishlists/${id}/`),
  getWishlist: () =>
    apiClient.get('/marketplace/wishlists/').then(unwrap),
  placeOrder: (data) =>
    apiClient.post('/marketplace/orders/', data).then((r) => r.data.data || r.data),
  getListingReviews: (listingId) =>
    apiClient.get('/marketplace/reviews/', { params: { listing: listingId } }).then(unwrap),
  createReview: (data) =>
    apiClient.post('/marketplace/reviews/', data).then((r) => r.data.data || r.data),
};
