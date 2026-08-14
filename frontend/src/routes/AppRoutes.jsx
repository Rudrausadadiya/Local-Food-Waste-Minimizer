import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { VendorLayout } from '../layouts/VendorLayout';
import { CustomerLayout } from '../layouts/CustomerLayout';
import { NgoLayout } from '../layouts/NgoLayout';
import { AdminLayout } from '../layouts/AdminLayout';
import { SkeletonTable } from '../components/ui/Skeleton';
import { useAuthStore } from '../stores/useAuthStore';

// Auth pages — not lazy (small, always needed)
import { LoginPage } from '../features/auth/pages/LoginPage';
import { SignupPage } from '../features/auth/pages/SignupPage';
import { PendingOnboardingPage } from '../features/auth/pages/PendingOnboardingPage';

const ForgotPasswordPage = lazy(() => import('../features/auth/pages/ForgotPasswordPage'));
const ResetPasswordPage  = lazy(() => import('../features/auth/pages/ResetPasswordPage'));
const VerifyEmailPage    = lazy(() => import('../features/auth/pages/VerifyEmailPage'));

// Lazy vendor pages
const VendorDashboardPage  = lazy(() => import('../features/business/pages/VendorDashboardPage'));
const InventoryListPage    = lazy(() => import('../features/inventory/pages/InventoryListPage'));
const VendorMarketplacePage= lazy(() => import('../features/marketplace/pages/VendorMarketplacePage'));
const CreateListingPage    = lazy(() => import('../features/marketplace/pages/CreateListingPage'));
const VendorOrdersPage     = lazy(() => import('../features/orders/pages/VendorOrdersPage'));
const VendorDonationsPage  = lazy(() => import('../features/donations/pages/VendorDonationsPage'));
const VendorAnalyticsPage  = lazy(() => import('../features/analytics/pages/VendorAnalyticsPage'));
const BranchManagementPage = lazy(() => import('../features/business/pages/BranchManagementPage'));

// Lazy customer pages
const BrowseMarketplacePage= lazy(() => import('../features/marketplace/pages/BrowseMarketplacePage'));
const ListingDetailPage    = lazy(() => import('../features/marketplace/pages/ListingDetailPage'));
const CustomerOrdersPage   = lazy(() => import('../features/orders/pages/CustomerOrdersPage'));
const WishlistPage         = lazy(() => import('../features/marketplace/pages/WishlistPage'));

// Lazy NGO pages
const NgoDashboardPage     = lazy(() => import('../features/donations/pages/NgoDashboardPage'));
const NgoBrowsePage        = lazy(() => import('../features/donations/pages/NgoBrowsePage'));
const NgoPickupsPage       = lazy(() => import('../features/donations/pages/NgoPickupsPage'));
const NgoImpactPage        = lazy(() => import('../features/donations/pages/NgoImpactPage'));

// Lazy Admin pages
const AdminDashboardPage   = lazy(() => import('../features/admin/pages/AdminDashboardPage'));
const AdminBusinessesPage  = lazy(() => import('../features/admin/pages/AdminBusinessesPage'));
const AdminListingsPage    = lazy(() => import('../features/admin/pages/AdminListingsPage'));
const AdminUsersPage       = lazy(() => import('../features/admin/pages/AdminUsersPage'));
const AdminAnalyticsPage   = lazy(() => import('../features/admin/pages/AdminAnalyticsPage'));

// Component: PageLoader
const PageLoader = () => (
  <div className="p-6">
    <SkeletonTable rows={5} cols={4} />
  </div>
);

// Component: RootRedirect
const RootRedirect = () => {
  const { isAuthenticated, user } = useAuthStore();
  if (!isAuthenticated || !user) return <Navigate to="/login" replace />;
  switch (user.role) {
    case 'VENDOR':   return <Navigate to="/vendor/dashboard" replace />;
    case 'NGO':      return <Navigate to="/ngo/dashboard" replace />;
    case 'CUSTOMER': return <Navigate to="/customer/browse" replace />;
    case 'ADMIN':    return <Navigate to="/admin/dashboard" replace />;
    default:         return <Navigate to="/login" replace />;
  }
};

// Component: AppRoutes
export const AppRoutes = () => (
  <Suspense fallback={<PageLoader />}>
    <Routes>
      {/* Root */}
      <Route path="/" element={<RootRedirect />} />

      {/* Auth */}
      <Route path="/login"                element={<LoginPage />} />
      <Route path="/signup"               element={<SignupPage />} />
      <Route path="/forgot-password"      element={<ForgotPasswordPage />} />
      <Route path="/reset-password"       element={<ResetPasswordPage />} />
      <Route path="/verify-email"         element={<VerifyEmailPage />} />
      <Route path="/onboarding/pending"   element={<PendingOnboardingPage />} />

      {/* ── VENDOR ── */}
      <Route path="/vendor/dashboard"
        element={<ProtectedRoute allowedRoles={['VENDOR']}><VendorLayout><VendorDashboardPage /></VendorLayout></ProtectedRoute>} />
      <Route path="/vendor/inventory"
        element={<ProtectedRoute allowedRoles={['VENDOR']}><VendorLayout><InventoryListPage /></VendorLayout></ProtectedRoute>} />
      <Route path="/vendor/marketplace"
        element={<ProtectedRoute allowedRoles={['VENDOR']}><VendorLayout><VendorMarketplacePage /></VendorLayout></ProtectedRoute>} />
      <Route path="/vendor/marketplace/new"
        element={<ProtectedRoute allowedRoles={['VENDOR']}><VendorLayout><CreateListingPage /></VendorLayout></ProtectedRoute>} />
      <Route path="/vendor/orders"
        element={<ProtectedRoute allowedRoles={['VENDOR']}><VendorLayout><VendorOrdersPage /></VendorLayout></ProtectedRoute>} />
      <Route path="/vendor/donations"
        element={<ProtectedRoute allowedRoles={['VENDOR']}><VendorLayout><VendorDonationsPage /></VendorLayout></ProtectedRoute>} />
      <Route path="/vendor/analytics"
        element={<ProtectedRoute allowedRoles={['VENDOR']}><VendorLayout><VendorAnalyticsPage /></VendorLayout></ProtectedRoute>} />
      <Route path="/vendor/branches"
        element={<ProtectedRoute allowedRoles={['VENDOR']}><VendorLayout><BranchManagementPage /></VendorLayout></ProtectedRoute>} />
      <Route path="/vendor/*" element={<Navigate to="/vendor/dashboard" replace />} />

      {/* ── CUSTOMER ── */}
      <Route path="/customer/browse"
        element={<ProtectedRoute allowedRoles={['CUSTOMER']}><CustomerLayout><BrowseMarketplacePage /></CustomerLayout></ProtectedRoute>} />
      <Route path="/customer/listing/:id"
        element={<ProtectedRoute allowedRoles={['CUSTOMER']}><CustomerLayout><ListingDetailPage /></CustomerLayout></ProtectedRoute>} />
      <Route path="/customer/orders"
        element={<ProtectedRoute allowedRoles={['CUSTOMER']}><CustomerLayout><CustomerOrdersPage /></CustomerLayout></ProtectedRoute>} />
      <Route path="/customer/saved"
        element={<ProtectedRoute allowedRoles={['CUSTOMER']}><CustomerLayout><WishlistPage /></CustomerLayout></ProtectedRoute>} />
      <Route path="/customer/*" element={<Navigate to="/customer/browse" replace />} />

      {/* ── NGO ── */}
      <Route path="/ngo/dashboard"
        element={<ProtectedRoute allowedRoles={['NGO']}><NgoLayout><NgoDashboardPage /></NgoLayout></ProtectedRoute>} />
      <Route path="/ngo/browse"
        element={<ProtectedRoute allowedRoles={['NGO']}><NgoLayout><NgoBrowsePage /></NgoLayout></ProtectedRoute>} />
      <Route path="/ngo/reservations"
        element={<ProtectedRoute allowedRoles={['NGO']}><NgoLayout><NgoPickupsPage /></NgoLayout></ProtectedRoute>} />
      <Route path="/ngo/impact"
        element={<ProtectedRoute allowedRoles={['NGO']}><NgoLayout><NgoImpactPage /></NgoLayout></ProtectedRoute>} />
      <Route path="/ngo/*" element={<Navigate to="/ngo/dashboard" replace />} />

      {/* ── ADMIN ── */}
      <Route path="/admin/dashboard"
        element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminLayout><AdminDashboardPage /></AdminLayout></ProtectedRoute>} />
      <Route path="/admin/businesses"
        element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminLayout><AdminBusinessesPage /></AdminLayout></ProtectedRoute>} />
      <Route path="/admin/listings"
        element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminLayout><AdminListingsPage /></AdminLayout></ProtectedRoute>} />
      <Route path="/admin/users"
        element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminLayout><AdminUsersPage /></AdminLayout></ProtectedRoute>} />
      <Route path="/admin/analytics"
        element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminLayout><AdminAnalyticsPage /></AdminLayout></ProtectedRoute>} />
      <Route path="/admin/*" element={<Navigate to="/admin/dashboard" replace />} />

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </Suspense>
);
