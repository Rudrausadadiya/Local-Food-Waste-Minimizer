import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/useAuthStore';

// Component: ForbiddenPage
const ForbiddenPage = ({ userRole, requiredRoles }) => (
  <div className="flex items-center justify-center h-full">
    <div className="text-center max-w-md p-8">
      <div className="w-16 h-16 rounded-2xl bg-red-100 dark:bg-red-900/20 flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h1 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-2">Access Restricted</h1>
      <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
        Your account role ({userRole}) does not have permission to access this area.
        This page is restricted to: {requiredRoles.join(', ')}.
      </p>
      <a href="/" className="text-sm text-emerald-600 hover:underline">Return to home</a>
    </div>
  </div>
);

// Component: ProtectedRoute
export const ProtectedRoute = ({ allowedRoles, children }) => {
  const { isAuthenticated, user } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if ((user.role === 'VENDOR' || user.role === 'NGO') && ['PENDING', 'REJECTED', 'SUSPENDED'].includes(user.business_status)) {
    return <Navigate to="/onboarding/pending" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    let userHome = '/customer/browse';
    if (user.role === 'VENDOR') userHome = '/vendor/dashboard';
    else if (user.role === 'NGO') userHome = '/ngo/dashboard';
    else if (user.role === 'ADMIN') userHome = '/admin/dashboard';

    return <Navigate to={userHome} replace />;
  }

  return children;
};
