import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Users, Search, ShieldCheck, Ban, Check, AlertTriangle } from 'lucide-react';
import { authApi } from '../../auth/api/authApi';
import { Button } from '../../../components/ui/Button';
import { SkeletonTable } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';
import { useToastStore } from '../../../stores/useToastStore';

// Component: AdminUsersPage
export const AdminUsersPage = () => {
  const [roleFilter, setRoleFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const { addToast } = useToastStore();
  const qc = useQueryClient();

  const { data: users, isLoading, error } = useQuery({
    queryKey: ['admin', 'users', roleFilter, searchQuery],
    queryFn: () => authApi.getAdminUsers({ role: roleFilter, search: searchQuery }),
  });

  const toggleStatusMutation = useMutation({
    mutationFn: ({ id, isActive }) => authApi.toggleUserStatus(id, isActive),
    onSuccess: (data, variables) => {
      addToast({
        title: variables.isActive ? 'Account Reactivated!' : 'Account Suspended!',
        description: `User account status has been updated to ${variables.isActive ? 'Active' : 'Suspended'}.`,
        variant: variables.isActive ? 'success' : 'error'
      });
      qc.invalidateQueries({ queryKey: ['admin', 'users'] });
    },
    onError: (err) => {
      addToast({
        title: 'Operation Failed',
        description: err?.response?.data?.detail || 'Could not update user status.',
        variant: 'error'
      });
    }
  });

  const usersList = Array.isArray(users) ? users : [];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Users className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
            User Account &amp; Privilege Control Center
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Ban/unban accounts, assign role privileges, and verify email credentials.
          </p>
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search users or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="border-b border-slate-200 dark:border-slate-800 flex gap-6">
        {['ALL', 'CUSTOMER', 'VENDOR', 'NGO', 'ADMIN'].map((r) => (
          <button
            key={r}
            onClick={() => setRoleFilter(r)}
            className={`pb-3 text-sm font-semibold border-b-2 transition-colors ${
              roleFilter === r
                ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            {r}
          </button>
        ))}
      </div>

      {error ? (
        <div className="p-6 rounded-2xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
          <div>
            <p className="font-bold">Failed to load user registry</p>
            <p className="text-xs text-red-500 mt-1">{error?.message || 'Could not fetch users from backend.'}</p>
          </div>
        </div>
      ) : isLoading ? (
        <SkeletonTable rows={5} cols={5} />
      ) : !usersList.length ? (
        <EmptyState
          icon={<Users className="w-8 h-8" />}
          title={`No ${roleFilter.toLowerCase()} users found`}
          description="Registered platform users will appear here."
        />
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
          <table className="w-full text-sm" aria-label="User registry">
            <thead className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-800">
              <tr>
                {['User Name', 'Email Address', 'Platform Role', 'Account Status', 'Admin Actions'].map((h) => (
                  <th key={h} className="text-left px-4 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {usersList.map((u) => {
                const fullName = `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.email || 'User';
                const initial = (u.first_name?.[0] || u.email?.[0] || 'U').toUpperCase();
                const isActive = u.is_active !== false;

                return (
                  <tr key={u.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                    <td className="px-4 py-3.5 font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <div className="w-8 h-8 rounded-xl bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 font-bold flex items-center justify-center text-xs">
                        {initial}
                      </div>
                      <div>
                        <p>{fullName}</p>
                        <p className="text-[10px] font-mono text-slate-400">{u.phone_number || 'No phone'}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-600 dark:text-slate-400">{u.email}</td>
                    <td className="px-4 py-3.5">
                      <span className={`text-[10px] font-extrabold px-2.5 py-1 rounded-full uppercase border ${
                        u.role === 'ADMIN' ? 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/80 dark:text-purple-300' :
                        u.role === 'VENDOR' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/80 dark:text-emerald-300' :
                        u.role === 'NGO' ? 'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950/80 dark:text-indigo-300' :
                        'bg-sky-50 text-sky-700 border-sky-200 dark:bg-sky-950/80 dark:text-sky-300'
                      }`}>
                        {u.role || 'CUSTOMER'}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 space-y-1">
                      <div className="flex items-center gap-1.5">
                        <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-1 rounded-full border ${
                          isActive
                            ? 'text-emerald-700 bg-emerald-50 border-emerald-300 dark:bg-emerald-950/80 dark:text-emerald-300'
                            : 'text-red-700 bg-red-50 border-red-300 dark:bg-red-950/80 dark:text-red-300'
                        }`}>
                          {isActive ? <ShieldCheck className="w-3 h-3" /> : <Ban className="w-3 h-3" />}
                          {isActive ? 'ACTIVE' : 'SUSPENDED'}
                        </span>
                        {u.business_status && u.business_status !== 'APPROVED' && (
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                            u.business_status === 'PENDING' ? 'bg-amber-50 text-amber-700 border-amber-300' : 'bg-red-50 text-red-700 border-red-300'
                          }`}>
                            {u.business_status}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3.5">
                      {u.business_status === 'PENDING' ? (
                        <Button
                          variant="primary"
                          size="xs"
                          className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold"
                          leftIcon={<Check className="w-3 h-3" />}
                          disabled={toggleStatusMutation.isPending}
                          onClick={() => toggleStatusMutation.mutate({ id: u.id, isActive: true })}
                        >
                          Approve Application
                        </Button>
                      ) : (
                        <Button
                          variant={isActive ? 'destructive' : 'primary'}
                          size="xs"
                          className={isActive ? 'font-bold' : 'bg-emerald-600 hover:bg-emerald-700 text-white font-bold'}
                          leftIcon={isActive ? <Ban className="w-3 h-3" /> : <Check className="w-3 h-3" />}
                          disabled={toggleStatusMutation.isPending}
                          onClick={() => toggleStatusMutation.mutate({ id: u.id, isActive: !isActive })}
                        >
                          {isActive ? 'Suspend Account' : 'Unsuspend Account'}
                        </Button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AdminUsersPage;
