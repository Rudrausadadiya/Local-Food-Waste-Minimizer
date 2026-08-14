import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Function: cn
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// Function: formatCurrency
export function formatCurrency(amount, currency = 'INR') {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency }).format(amount || 0);
}

// Function: formatDate
export function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// Function: formatDateTime
export function formatDateTime(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
}

// Function: getTimeUntil
export function getTimeUntil(dateStr) {
  if (!dateStr) return { hours: 0, minutes: 0, seconds: 0, expired: true };
  const diff = new Date(dateStr).getTime() - Date.now();
  if (diff <= 0) return { hours: 0, minutes: 0, seconds: 0, expired: true };
  const hours = Math.floor(diff / 3_600_000);
  const minutes = Math.floor((diff % 3_600_000) / 60_000);
  const seconds = Math.floor((diff % 60_000) / 1_000);
  return { hours, minutes, seconds, expired: false };
}

// Function: getDiscountPercent
export function getDiscountPercent(original, discounted) {
  if (!original) return 0;
  return Math.round(((original - discounted) / original) * 100);
}

// Function: getListingCoordinates
export function getListingCoordinates(listing) {
  if (!listing) return { lat: 23.0225, lng: 72.5714 };

  // Check branch address, business address, or direct business coordinates
  const rawLat = listing.branch?.address?.latitude || 
                 listing.business?.address?.latitude || 
                 listing.business?.latitude;

  const rawLng = listing.branch?.address?.longitude || 
                 listing.business?.address?.longitude || 
                 listing.business?.longitude;

  if (rawLat && rawLng && !isNaN(Number(rawLat)) && !isNaN(Number(rawLng))) {
    return { lat: Number(rawLat), lng: Number(rawLng) };
  }

  // Deterministic fallback based on listing ID string hash so it's 100% consistent across all pages
  const seedStr = String(listing.id || listing.listing_title || 'default-seed');
  let hash = 0;
  for (let i = 0; i < seedStr.length; i++) {
    hash = (hash << 5) - hash + seedStr.charCodeAt(i);
    hash |= 0;
  }
  const latOffset = ((Math.abs(hash) % 100) - 50) * 0.0004;
  const lngOffset = ((Math.abs(hash >> 3) % 100) - 50) * 0.0004;

  return {
    lat: Number((23.0225 + latOffset).toFixed(6)),
    lng: Number((72.5714 + lngOffset).toFixed(6)),
  };
}
