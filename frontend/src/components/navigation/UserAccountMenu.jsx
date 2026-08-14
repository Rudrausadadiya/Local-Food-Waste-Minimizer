import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  User, Settings, Sun, Moon, LogOut, ChevronDown, Shield, Check,
  Camera, Phone, Mail, Sparkles, Loader2, Upload, Lock, AlertTriangle,
  HelpCircle, BookOpen, ShoppingBag, Store, HeartHandshake, Key, Trash2,
  ClipboardList, MapPin, Home, Briefcase, Plus, CheckCircle
} from 'lucide-react';
import { useAuthStore } from '../../stores/useAuthStore';
import { useThemeStore } from '../../stores/useThemeStore';
import { useToastStore } from '../../stores/useToastStore';
import { authApi } from '../../features/auth/api/authApi';
import { ordersApi } from '../../features/orders/api/ordersApi';
import { businessApi } from '../../features/business/api/businessApi';
import { Input, PasswordInput } from '../ui/Input';
import { Button } from '../ui/Button';
import { StatusBadge } from '../ui/Badge';
import { LiveMapPicker } from '../ui/LiveMapPicker';
import { cn, formatCurrency, formatDateTime } from '../../lib/utils';

const AVATAR_PRESETS = [
  'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&auto=format&fit=crop&q=80',
];

// Function: getInitialAddressesForUser
const getInitialAddressesForUser = (u) => {
  // New users start with an empty address list for data privacy
  return [];
};

// Component: UserAccountMenu
export const UserAccountMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [showOrderHistoryModal, setShowOrderHistoryModal] = useState(false);
  const [showAddressModal, setShowAddressModal] = useState(false);
  const [showAddAddressForm, setShowAddAddressForm] = useState(false);
  const [showDeleteConfirmModal, setShowDeleteConfirmModal] = useState(false);

  const [helpTab, setHelpTab] = useState('getting-started');

  const menuRef = useRef(null);
  const fileInputRef = useRef(null);

  const { user, updateUser, logout } = useAuthStore();
  const { resolvedTheme, toggleTheme } = useThemeStore();
  const { addToast } = useToastStore();
  const navigate = useNavigate();

  // User-specific storage key for saved addresses
  const storageKey = user ? `fw_saved_addresses_${user.id || user.email}` : 'fw_saved_addresses_guest';

  // Address state per user account
  const [savedAddresses, setSavedAddresses] = useState(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      return stored ? JSON.parse(stored) : getInitialAddressesForUser(user);
    } catch {
      return getInitialAddressesForUser(user);
    }
  });

  // Re-hydrate savedAddresses when switching user accounts
  useEffect(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      setSavedAddresses(stored ? JSON.parse(stored) : getInitialAddressesForUser(user));
    } catch {
      setSavedAddresses(getInitialAddressesForUser(user));
    }
  }, [user?.id, user?.email, user?.role, storageKey]);

  // Sync savedAddresses to user's localStorage entry
  useEffect(() => {
    try {
      // Remove old legacy shared key if it exists
      localStorage.removeItem('fw_saved_addresses');
      localStorage.setItem(storageKey, JSON.stringify(savedAddresses));
    } catch (e) {
      console.warn('Failed to save addresses to localStorage:', e);
    }
  }, [savedAddresses, storageKey]);

  const [newAddrTag, setNewAddrTag] = useState('HOME');
  const [newAddrLine1, setNewAddrLine1] = useState('');
  const [newAddrLandmark, setNewAddrLandmark] = useState('');
  const [newAddrCity, setNewAddrCity] = useState('');
  const [newAddrZip, setNewAddrZip] = useState('');
  const [newAddrDefault, setNewAddrDefault] = useState(false);
  const [detectedCoords, setDetectedCoords] = useState({ lat: 23.0225, lng: 72.5714 });
  const [editingAddressId, setEditingAddressId] = useState(null);

  // Local form state for profile modal
  const [firstName, setFirstName] = useState(user?.first_name || '');
  const [lastName, setLastName] = useState(user?.last_name || '');
  const [phoneNumber, setPhoneNumber] = useState(user?.phone_number || '');
  const [profileImage, setProfileImage] = useState(user?.profile_image || '');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [deletePassword, setDeletePassword] = useState('');

  const isPhoneChanged = phoneNumber !== (user?.phone_number || '');

  // Fetch Order History for customer or vendor orders
  const { data: customerOrders, isLoading: ordersLoading } = useQuery({
    queryKey: ['orders', 'customer', 'history'],
    queryFn: ordersApi.getCustomerOrders,
    enabled: showOrderHistoryModal,
  });

  // Keep local state in sync when user store changes or modal opens
  useEffect(() => {
    if (showSettingsModal && user) {
      setFirstName(user.first_name || '');
      setLastName(user.last_name || '');
      setPhoneNumber(user.phone_number || '');
      setProfileImage(user.profile_image || '');
      setConfirmPassword('');
    }
  }, [showSettingsModal, user]);

  // Close dropdown menu on click outside
  useEffect(() => {
    // Function: handleClickOutside
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Function: handleLogout
  const handleLogout = () => {
    setIsOpen(false);
    logout();
    addToast({ title: 'Signed Out', description: 'You have been logged out safely.', variant: 'info' });
    navigate('/login');
  };

  // Profile update mutation
  const updateProfileMutation = useMutation({
    mutationFn: (data) => authApi.updateProfile(data),
    onSuccess: (updatedData) => {
      const newUser = updatedData?.user || updatedData || {
        first_name: firstName,
        last_name: lastName,
        phone_number: phoneNumber,
        profile_image: profileImage,
      };
      updateUser(newUser);
      addToast({ title: 'Profile Updated!', description: 'Your personal details were saved successfully.', variant: 'success' });
      setShowSettingsModal(false);
      setConfirmPassword('');
    },
    onError: (err) => {
      addToast({
        title: 'Update Failed',
        description: err?.response?.data?.detail || err?.response?.data?.message || 'Could not save profile changes.',
        variant: 'error'
      });
    },
  });

  // Account deletion mutation
  const deactivateAccountMutation = useMutation({
    mutationFn: () => authApi.deactivateAccount(),
    onSuccess: () => {
      setShowDeleteConfirmModal(false);
      setShowSettingsModal(false);
      logout();
      addToast({ title: 'Account Deactivated', description: 'Your account has been deleted successfully.', variant: 'info' });
      navigate('/login');
    },
    onError: (err) => {
      addToast({
        title: 'Deactivation Failed',
        description: err?.response?.data?.detail || 'Could not deactivate account. Please try again.',
        variant: 'error'
      });
    },
  });

  // Function: handleEditAddressClick
  const handleEditAddressClick = (addr) => {
    setEditingAddressId(addr.id);
    setNewAddrTag(addr.tag || 'HOME');
    setNewAddrLine1(addr.line1 || '');
    setNewAddrLandmark(addr.landmark || '');
    setNewAddrCity(addr.city || '');
    setNewAddrZip(addr.zip || '');
    setNewAddrDefault(addr.isDefault || false);
    if (addr.lat && addr.lng) {
      setDetectedCoords({ lat: addr.lat, lng: addr.lng });
    }
    setShowAddAddressForm(true);
  };

  // Function: handleAddAddress
  const handleAddAddress = (e) => {
    e.preventDefault();
    if (!newAddrLine1.trim() || !newAddrCity.trim()) {
      addToast({ title: 'Missing details', description: 'Street address and city are required.', variant: 'error' });
      return;
    }

    if (editingAddressId) {
      // Editing existing saved address
      setSavedAddresses((prev) =>
        prev.map((a) => {
          if (a.id === editingAddressId) {
            return {
              ...a,
              tag: newAddrTag,
              line1: newAddrLine1,
              landmark: newAddrLandmark,
              city: newAddrCity,
              zip: newAddrZip,
              isDefault: newAddrDefault ? true : a.isDefault,
              lat: detectedCoords.lat,
              lng: detectedCoords.lng,
            };
          }
          return newAddrDefault ? { ...a, isDefault: false } : a;
        })
      );
      addToast({ title: 'Address Updated!', description: 'Your delivery location was saved.', variant: 'success' });
    } else {
      // Adding brand new address
      const newEntry = {
        id: `addr-${Date.now()}`,
        tag: newAddrTag,
        line1: newAddrLine1,
        landmark: newAddrLandmark,
        city: newAddrCity,
        zip: newAddrZip,
        lat: detectedCoords.lat,
        lng: detectedCoords.lng,
        isDefault: newAddrDefault || savedAddresses.length === 0,
      };

      let updated = [...savedAddresses];
      if (newEntry.isDefault) {
        updated = updated.map((a) => ({ ...a, isDefault: false }));
      }
      updated.push(newEntry);

      setSavedAddresses(updated);
      addToast({ title: 'Address Saved', description: 'New address added to your profile.', variant: 'success' });
    }

    setShowAddAddressForm(false);
    setEditingAddressId(null);
    setNewAddrLine1('');
    setNewAddrLandmark('');
    setNewAddrCity('');
    setNewAddrZip('');
  };

  // Function: handleSetDefaultAddress
  const handleSetDefaultAddress = (id) => {
    setSavedAddresses((prev) =>
      prev.map((a) => ({ ...a, isDefault: a.id === id }))
    );
    addToast({ title: 'Default Address Updated', variant: 'success' });
  };

  // Function: handleDeleteAddress
  const handleDeleteAddress = (id) => {
    setSavedAddresses((prev) => prev.filter((a) => a.id !== id));
    addToast({ title: 'Address Removed', variant: 'info' });
  };

  // Function: handleSaveProfile
  const handleSaveProfile = (e) => {
    e.preventDefault();

    if (isPhoneChanged && !confirmPassword.trim()) {
      addToast({
        title: 'Password Required',
        description: 'You must enter your current password to authorize phone number update.',
        variant: 'error'
      });
      return;
    }

    updateProfileMutation.mutate({
      first_name: firstName,
      last_name: lastName,
      phone_number: phoneNumber,
      profile_image: profileImage,
      ...(isPhoneChanged ? { password: confirmPassword } : {})
    });
  };

  // Function: handleConfirmDelete
  const handleConfirmDelete = (e) => {
    e.preventDefault();
    if (!deletePassword.trim()) {
      addToast({
        title: 'Password Required',
        description: 'Enter your password to confirm account deletion.',
        variant: 'error'
      });
      return;
    }
    deactivateAccountMutation.mutate();
  };

  // Function: handleImageFileChange
  const handleImageFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      addToast({ title: 'Image too large', description: 'Please select an image smaller than 2MB.', variant: 'error' });
      return;
    }
    const reader = new FileReader();
    reader.onloadend = () => {
      setProfileImage(reader.result);
    };
    reader.readAsDataURL(file);
  };

  // Function: getRoleBadgeColor
  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'VENDOR': return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
      case 'NGO': return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800';
      case 'ADMIN': return 'bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300 border-purple-200 dark:border-purple-800';
      default: return 'bg-sky-100 text-sky-800 dark:bg-sky-950/60 dark:text-sky-300 border-sky-200 dark:border-sky-800';
    }
  };

  // Function: getAvatarBg
  const getAvatarBg = (role) => {
    switch (role) {
      case 'NGO': return 'bg-indigo-600';
      case 'ADMIN': return 'bg-purple-600';
      case 'CUSTOMER': return 'bg-sky-600';
      default: return 'bg-emerald-600';
    }
  };

  const currentAvatar = profileImage || user?.profile_image;
  const initials = `${user?.first_name?.[0] || 'U'}${user?.last_name?.[0] || ''}`;

  return (
    <>
    <div className="relative" ref={menuRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="flex items-center gap-2 p-1 pl-1.5 pr-2.5 rounded-full border border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900/80 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
        aria-label="User account menu"
        aria-expanded={isOpen}
      >
        {currentAvatar ? (
          <img src={currentAvatar} alt="Profile" className="w-7 h-7 rounded-full object-cover shadow-sm border border-emerald-500" />
        ) : (
          <div className={cn("w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-sm", getAvatarBg(user?.role))}>
            {initials}
          </div>
        )}
        <span className="text-xs font-semibold text-slate-700 dark:text-slate-200 max-w-[100px] truncate hidden sm:inline">
          {user?.first_name || 'Account'}
        </span>
        <ChevronDown className={cn("w-3.5 h-3.5 text-slate-400 transition-transform duration-200", isOpen && "rotate-180")} />
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.96 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className="absolute right-0 top-full mt-2 w-72 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl z-[10000] overflow-hidden"
          >
            {/* Profile Header Banner */}
            <div className="p-4 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800/80 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-start gap-3">
                {currentAvatar ? (
                  <img src={currentAvatar} alt="Profile" className="w-10 h-10 rounded-full object-cover shadow-md flex-shrink-0 border-2 border-emerald-500" />
                ) : (
                  <div className={cn("w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold shadow-md flex-shrink-0", getAvatarBg(user?.role))}>
                    {initials}
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold text-slate-900 dark:text-slate-100 truncate">
                    {user?.first_name} {user?.last_name}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 truncate mb-1.5">
                    {user?.email}
                  </p>
                  <span className={cn("inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-md border tracking-wide uppercase", getRoleBadgeColor(user?.role))}>
                    <Shield className="w-2.5 h-2.5" />
                    {user?.role_display || user?.role}
                  </span>
                </div>
              </div>
            </div>

            {/* Menu Options Group */}
            <div className="p-2 space-y-1">
              {/* Order History Option (Customer Only) */}
              {user?.role === 'CUSTOMER' && (
                <button
                  onClick={() => {
                    setIsOpen(false);
                    setShowOrderHistoryModal(true);
                  }}
                  className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                      <ClipboardList className="w-3.5 h-3.5" />
                    </div>
                    <span>Order History</span>
                  </div>
                  <span className="text-[10px] text-emerald-600 font-bold bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full">Past Orders</span>
                </button>
              )}

              {/* Saved Addresses Option (Only for Customers and Vendors) */}
              {(user?.role === 'CUSTOMER' || user?.role === 'VENDOR') && (
                <button
                  onClick={() => {
                    setIsOpen(false);
                    setShowAddressModal(true);
                  }}
                  className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-lg bg-sky-50 dark:bg-sky-950/40 text-sky-600 dark:text-sky-400 flex items-center justify-center">
                      <MapPin className="w-3.5 h-3.5" />
                    </div>
                    <span>Saved Addresses</span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">{savedAddresses.length} saved</span>
                </button>
              )}

              {/* Account Settings Option */}
              <button
                onClick={() => {
                  setIsOpen(false);
                  setShowSettingsModal(true);
                }}
                className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-500 dark:text-slate-400">
                    <Settings className="w-3.5 h-3.5" />
                  </div>
                  <span>Account Settings</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">Edit Profile</span>
              </button>

              {/* Help & Guide Option */}
              <button
                onClick={() => {
                  setIsOpen(false);
                  setShowHelpModal(true);
                }}
                className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                    <HelpCircle className="w-3.5 h-3.5" />
                  </div>
                  <span>Help & User Guide</span>
                </div>
                <span className="text-[10px] text-indigo-500 font-semibold">Docs</span>
              </button>

              {/* Theme Switcher Toggle Option */}
              <button
                onClick={toggleTheme}
                className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 flex items-center justify-center">
                    {resolvedTheme === 'dark' ? <Moon className="w-3.5 h-3.5" /> : <Sun className="w-3.5 h-3.5" />}
                  </div>
                  <span>Appearance</span>
                </div>
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full capitalize">
                  {resolvedTheme === 'dark' ? 'Dark' : 'Light'} Mode
                </span>
              </button>
            </div>

            {/* Divider */}
            <div className="border-t border-slate-100 dark:border-slate-800" />

            {/* Logout Option */}
            <div className="p-2">
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
              >
                <div className="w-7 h-7 rounded-lg bg-red-100 dark:bg-red-950/50 text-red-600 dark:text-red-400 flex items-center justify-center">
                  <LogOut className="w-3.5 h-3.5" />
                </div>
                <span>Sign Out</span>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>

    {/* All modals rendered via Portal to escape the backdrop-filter stacking context */}
    {createPortal(
      <>
      {/* Zomato-style Order History Modal */}
      <AnimatePresence>
        {showOrderHistoryModal && (
          <div className="fixed inset-0 z-[10000] flex items-start justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-2xl m-auto bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-2xl overflow-hidden"
            >
              <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-emerald-100 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                    <ClipboardList className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 dark:text-slate-100 text-lg">My Order & Rescue History</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">View past orders, reserved items, pricing & claim codes</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowOrderHistoryModal(false)}
                  className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  ✕
                </button>
              </div>

              <div className="p-6 max-h-[65vh] overflow-y-auto space-y-4">
                {ordersLoading ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="h-20 bg-slate-100 dark:bg-slate-800 rounded-2xl animate-pulse" />
                    ))}
                  </div>
                ) : !customerOrders?.length ? (
                  <div className="text-center py-10 space-y-3">
                    <ShoppingBag className="w-10 h-10 text-slate-300 dark:text-slate-700 mx-auto" />
                    <p className="font-bold text-slate-800 dark:text-slate-200">No past orders yet</p>
                    <p className="text-xs text-slate-400 max-w-sm mx-auto">
                      Explore nearby surplus food offers to place your first reservation and rescue food.
                    </p>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => {
                        setShowOrderHistoryModal(false);
                        navigate('/customer/browse');
                      }}
                    >
                      Browse Marketplace
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {customerOrders.map((order) => (
                      <div
                        key={order.id}
                        className="bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200/70 dark:border-slate-800 p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                      >
                        <div className="space-y-1 min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <StatusBadge status={order.status} />
                            <span className="text-[11px] text-slate-400 tabular-nums">{formatDateTime(order.created_at)}</span>
                          </div>
                          <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm truncate">
                            {order.listing?.listing_title || 'Surplus Food Order'}
                          </h4>
                          <p className="text-xs text-slate-500 flex items-center gap-1">
                            <Store className="w-3 h-3 text-slate-400" />
                            {order.listing?.business?.business_name || 'Partner Merchant'}
                          </p>
                        </div>

                        <div className="flex items-center gap-4 flex-shrink-0 w-full sm:w-auto justify-between sm:justify-end border-t sm:border-t-0 pt-2 sm:pt-0 border-slate-200/60 dark:border-slate-700/50">
                          <div className="text-left sm:text-right">
                            <p className="text-xs text-slate-400">Total Paid</p>
                            <p className="font-bold text-emerald-600 dark:text-emerald-400 text-sm tabular-nums">
                              {formatCurrency(Number(order.total_price))}
                            </p>
                          </div>
                          <div className="bg-emerald-100 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800 px-3 py-1.5 rounded-xl text-center">
                            <p className="text-[9px] font-bold uppercase text-emerald-700 dark:text-emerald-300">Claim Code</p>
                            <p className="font-mono font-bold text-xs text-emerald-900 dark:text-emerald-200">#{order.claim_code}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex justify-end">
                <Button variant="outline" size="sm" onClick={() => setShowOrderHistoryModal(false)}>
                  Close History
                </Button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Zomato-style Saved Addresses Modal */}
      <AnimatePresence>
        {showAddressModal && (
          <div className="fixed inset-0 z-[10000] flex items-start justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-xl m-auto bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-2xl overflow-hidden"
            >
              <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-sky-100 dark:bg-sky-950/50 text-sky-600 dark:text-sky-400 flex items-center justify-center">
                    <MapPin className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 dark:text-slate-100 text-lg">Saved Delivery & Pickup Addresses</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Manage saved pickup and delivery locations</p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setShowAddressModal(false);
                    setShowAddAddressForm(false);
                  }}
                  className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  ✕
                </button>
              </div>

              <div className="p-6 max-h-[65vh] overflow-y-auto space-y-4">
                {!showAddAddressForm ? (
                  <>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-bold text-slate-700 dark:text-slate-300">My Saved Locations ({savedAddresses.length})</span>
                      <button
                        onClick={() => {
                          setEditingAddressId(null);
                          setNewAddrLine1('');
                          setNewAddrLandmark('');
                          setNewAddrCity('');
                          setNewAddrZip('');
                          setShowAddAddressForm(true);
                        }}
                        className="inline-flex items-center gap-1 text-xs font-bold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400"
                      >
                        <Plus className="w-3.5 h-3.5" /> Add New Address
                      </button>
                    </div>

                    <div className="space-y-3">
                      {savedAddresses.map((addr) => (
                        <div
                          key={addr.id}
                          className={cn(
                            "p-4 rounded-2xl border transition-all flex items-start justify-between gap-4",
                            addr.isDefault
                              ? "bg-emerald-50/60 dark:bg-emerald-950/30 border-emerald-300 dark:border-emerald-800"
                              : "bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800"
                          )}
                        >
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 uppercase">
                                {addr.tag === 'HOME' && <Home className="w-3 h-3 text-emerald-600" />}
                                {addr.tag === 'WORK' && <Briefcase className="w-3 h-3 text-sky-600" />}
                                {addr.tag !== 'HOME' && addr.tag !== 'WORK' && <MapPin className="w-3 h-3 text-amber-600" />}
                                {addr.tag}
                              </span>
                              {addr.isDefault && (
                                <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-300 bg-emerald-200/60 dark:bg-emerald-900/60 px-2 py-0.5 rounded-md">
                                  Default Address
                                </span>
                              )}
                            </div>
                            <p className="font-bold text-slate-900 dark:text-slate-100 text-xs mt-1">{addr.line1}</p>
                            {addr.landmark && <p className="text-[11px] text-slate-500">Landmark: {addr.landmark}</p>}
                            <p className="text-[11px] text-slate-400">{addr.city}, Zip: {addr.zip}</p>
                          </div>

                          <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => handleEditAddressClick(addr)}
                                className="text-[11px] text-sky-600 hover:text-sky-700 dark:text-sky-400 hover:underline font-semibold"
                              >
                                ✏️ Edit
                              </button>
                              {!addr.isDefault && (
                                <button
                                  onClick={() => handleSetDefaultAddress(addr.id)}
                                  className="text-[11px] text-emerald-600 hover:underline font-semibold"
                                >
                                  Set Default
                                </button>
                              )}
                            </div>
                            <button
                              onClick={() => handleDeleteAddress(addr.id)}
                              className="text-[11px] text-red-500 hover:underline font-medium"
                            >
                              Remove
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  /* Add / Edit Address Form */
                  <form onSubmit={handleAddAddress} className="space-y-4">
                    <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                      <h4 className="font-bold text-slate-900 dark:text-slate-100 text-xs uppercase tracking-wider">
                        {editingAddressId ? '✏️ Edit Delivery Location' : '➕ Add New Delivery Location'}
                      </h4>
                      <button
                        type="button"
                        onClick={() => {
                          setShowAddAddressForm(false);
                          setEditingAddressId(null);
                        }}
                        className="text-xs text-slate-400 hover:underline"
                      >
                        Back to Saved
                      </button>
                    </div>

                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Address Type Tag</label>
                      <div className="flex gap-2">
                        {['HOME', 'WORK', 'BRANCH', 'OTHER'].map((tag) => (
                          <button
                            key={tag}
                            type="button"
                            onClick={() => setNewAddrTag(tag)}
                            className={cn(
                              "px-3 py-1.5 rounded-xl border text-xs font-bold transition-all",
                              newAddrTag === tag
                                ? "border-emerald-500 bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300"
                                : "border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400"
                            )}
                          >
                            {tag}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Interactive Map Picker Section */}
                    <div className="p-3.5 rounded-2xl bg-slate-100/70 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-emerald-600" /> Real-time Interactive GPS Map
                        </span>
                        <span className="text-[10px] text-emerald-600 font-mono font-bold bg-emerald-100 dark:bg-emerald-950/60 px-2 py-0.5 rounded-md flex items-center gap-1">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span> Live Map Active
                        </span>
                      </div>
                      
                      {/* Real-time Interactive Leaflet Map */}
                      <LiveMapPicker
                        initialLat={detectedCoords.lat}
                        initialLng={detectedCoords.lng}
                        height="260px"
                        allowSearch={true}
                        allowLiveTracking={true}
                        onLocationSelect={(details) => {
                          if (details) {
                            setNewAddrLine1(details.line1);
                            setNewAddrLandmark(details.landmark);
                            setNewAddrCity(details.city);
                            setNewAddrZip(details.zip);
                          }
                        }}
                      />
                    </div>

                    <Input
                      label="Street Address / House / Flat No."
                      placeholder="e.g. SG Highway, Bodakdev"
                      value={newAddrLine1}
                      onChange={(e) => setNewAddrLine1(e.target.value)}
                      required
                    />

                    <Input
                      label="Landmark / Floor"
                      placeholder="e.g. Opposite Iscon Mega Mall"
                      value={newAddrLandmark}
                      onChange={(e) => setNewAddrLandmark(e.target.value)}
                    />

                    <div className="grid grid-cols-2 gap-3">
                      <Input
                        label="City"
                        placeholder="e.g. Ahmedabad"
                        value={newAddrCity}
                        onChange={(e) => setNewAddrCity(e.target.value)}
                        required
                      />
                      <Input
                        label="Postal Code / Zip"
                        placeholder="e.g. 380054"
                        value={newAddrZip}
                        onChange={(e) => setNewAddrZip(e.target.value)}
                      />
                    </div>

                    <label className="flex items-center gap-2 text-xs font-medium text-slate-700 dark:text-slate-300 cursor-pointer pt-1">
                      <input
                        type="checkbox"
                        checked={newAddrDefault}
                        onChange={(e) => setNewAddrDefault(e.target.checked)}
                        className="rounded text-emerald-600 focus:ring-emerald-500"
                      />
                      Set as Default Delivery Address
                    </label>

                    <div className="flex justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
                      <Button
                        variant="outline"
                        size="sm"
                        type="button"
                        onClick={() => {
                          setShowAddAddressForm(false);
                          setEditingAddressId(null);
                        }}
                      >
                        Cancel
                      </Button>
                      <Button variant="primary" size="sm" type="submit">
                        {editingAddressId ? 'Save Changes' : 'Save Address'}
                      </Button>
                    </div>
                  </form>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Account Settings Modal */}
      <AnimatePresence>
        {showSettingsModal && (
          <div className="fixed inset-0 z-[10000] flex items-start justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-lg m-auto bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-2xl overflow-hidden"
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-emerald-100 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                    <User className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 dark:text-slate-100 text-lg">Account Profile Settings</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Update avatar, name, and phone number</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowSettingsModal(false)}
                  className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                  aria-label="Close settings"
                >
                  ✕
                </button>
              </div>

              {/* Modal Body / Form */}
              <form onSubmit={handleSaveProfile} className="p-6 space-y-6">
                {/* Profile Picture Upload Section */}
                <div className="flex flex-col items-center gap-4 p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800">
                  <div className="relative group">
                    {profileImage ? (
                      <img
                        src={profileImage}
                        alt="Profile preview"
                        className="w-20 h-20 rounded-full object-cover border-4 border-white dark:border-slate-900 shadow-md"
                      />
                    ) : (
                      <div className={cn("w-20 h-20 rounded-full flex items-center justify-center text-white text-2xl font-bold border-4 border-white dark:border-slate-900 shadow-md", getAvatarBg(user?.role))}>
                        {initials}
                      </div>
                    )}
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="absolute bottom-0 right-0 p-2 rounded-full bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg transition-transform duration-150 hover:scale-110"
                      title="Upload profile picture"
                    >
                      <Camera className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleImageFileChange}
                    accept="image/*"
                    className="hidden"
                  />

                  <div className="text-center space-y-1">
                    <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">Profile Picture</p>
                    <div className="flex items-center justify-center gap-2">
                      <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className="inline-flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400 hover:underline font-medium"
                      >
                        <Upload className="w-3 h-3" /> Upload File
                      </button>
                      {profileImage && (
                        <button
                          type="button"
                          onClick={() => setProfileImage('')}
                          className="text-xs text-red-500 hover:underline font-medium ml-2"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Preset Avatars */}
                  <div className="space-y-1.5 pt-2 border-t border-slate-200/60 dark:border-slate-700/50 w-full text-center">
                    <p className="text-[11px] text-slate-400">Or choose a preset avatar:</p>
                    <div className="flex justify-center gap-2">
                      {AVATAR_PRESETS.map((presetUrl, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => setProfileImage(presetUrl)}
                          className={cn(
                            "w-8 h-8 rounded-full overflow-hidden border-2 transition-transform hover:scale-110",
                            profileImage === presetUrl ? "border-emerald-500 scale-110 shadow-sm" : "border-transparent opacity-70 hover:opacity-100"
                          )}
                        >
                          <img src={presetUrl} alt={`Preset ${idx + 1}`} className="w-full h-full object-cover" />
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Form Fields: First Name, Last Name, Phone */}
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <Input
                      label="First Name"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      placeholder="First name"
                      required
                    />
                    <Input
                      label="Last Name"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      placeholder="Last name"
                      required
                    />
                  </div>

                  <Input
                    label="Phone Number"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    placeholder="+1 (555) 000-0000"
                    prefixIcon={<Phone className="w-4 h-4 text-slate-400" />}
                  />

                  {/* Password Authorization Box if Phone Number Changed */}
                  <AnimatePresence>
                    {isPhoneChanged && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/60 space-y-2 overflow-hidden"
                      >
                        <div className="flex items-center gap-2 text-xs font-bold text-amber-800 dark:text-amber-300">
                          <Lock className="w-4 h-4 text-amber-600" />
                          <span>Password Required for Phone Number Update</span>
                        </div>
                        <p className="text-[11px] text-amber-700 dark:text-amber-400">
                          To protect your account security, enter your current password to authorize this phone number update.
                        </p>
                        <PasswordInput
                          label="Current Password"
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          placeholder="Enter your current password"
                          required
                        />
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Email & Role (Info/Readonly) */}
                  <div className="p-3.5 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200/60 dark:border-slate-800 space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-500 flex items-center gap-1.5">
                        <Mail className="w-3.5 h-3.5 text-slate-400" /> Email Address
                      </span>
                      <span className="font-semibold font-mono text-slate-800 dark:text-slate-200">{user?.email}</span>
                    </div>
                    <div className="flex justify-between items-center text-xs pt-2 border-t border-slate-200/50 dark:border-slate-700/50">
                      <span className="text-slate-500 flex items-center gap-1.5">
                        <Shield className="w-3.5 h-3.5 text-slate-400" /> Account Role
                      </span>
                      <span className={cn("text-[10px] font-bold px-2 py-0.5 rounded-md border uppercase tracking-wider", getRoleBadgeColor(user?.role))}>
                        {user?.role_display || user?.role}
                      </span>
                    </div>
                  </div>

                  {/* Theme Mode Selector inside modal */}
                  <div className="space-y-2 pt-2">
                    <label className="block text-xs font-semibold text-slate-800 dark:text-slate-200">
                      Theme Preference
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        type="button"
                        onClick={() => resolvedTheme !== 'light' && toggleTheme()}
                        className={cn(
                          "flex items-center justify-center gap-2 p-3 rounded-2xl border text-xs font-semibold transition-all",
                          resolvedTheme === 'light'
                            ? "border-emerald-500 bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 shadow-sm"
                            : "border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
                        )}
                      >
                        <Sun className="w-4 h-4" /> Light Mode
                      </button>
                      <button
                        type="button"
                        onClick={() => resolvedTheme !== 'dark' && toggleTheme()}
                        className={cn(
                          "flex items-center justify-center gap-2 p-3 rounded-2xl border text-xs font-semibold transition-all",
                          resolvedTheme === 'dark'
                            ? "border-emerald-500 bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 shadow-sm"
                            : "border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
                        )}
                      >
                        <Moon className="w-4 h-4" /> Dark Mode
                      </button>
                    </div>
                  </div>

                  {/* Danger Zone: Delete Account */}
                  <div className="p-4 rounded-2xl bg-red-50/70 dark:bg-red-950/20 border border-red-200 dark:border-red-900/40 space-y-2 pt-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs font-bold text-red-900 dark:text-red-300 flex items-center gap-1.5">
                          <Trash2 className="w-3.5 h-3.5 text-red-600" /> Danger Zone: Delete Account
                        </p>
                        <p className="text-[11px] text-red-700 dark:text-red-400 mt-0.5">
                          Permanently deactivate your account and revoke platform access.
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => setShowDeleteConfirmModal(true)}
                        className="px-3 py-1.5 rounded-xl bg-red-600 text-white text-xs font-bold hover:bg-red-700 transition-colors flex-shrink-0"
                      >
                        Delete Account
                      </button>
                    </div>
                  </div>
                </div>

                {/* Form Actions */}
                <div className="pt-4 flex gap-3 justify-end border-t border-slate-100 dark:border-slate-800">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowSettingsModal(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    loading={updateProfileMutation.isPending}
                  >
                    Save Changes
                  </Button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Delete Account Confirmation Modal */}
      <AnimatePresence>
        {showDeleteConfirmModal && (
          <div className="fixed inset-0 z-50 flex items-start justify-center p-4 overflow-y-auto bg-black/70 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-md m-auto bg-white dark:bg-slate-900 border border-red-200 dark:border-red-900 rounded-3xl shadow-2xl p-6 space-y-5"
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400 flex items-center justify-center flex-shrink-0">
                  <AlertTriangle className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 dark:text-slate-100 text-lg">Confirm Account Deletion</h3>
                  <p className="text-xs text-red-600 dark:text-red-400 font-medium">This action cannot be undone</p>
                </div>
              </div>

              <div className="space-y-3 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                <p>
                  Deactivating your account will immediately:
                </p>
                <ul className="list-disc pl-5 space-y-1 text-slate-700 dark:text-slate-300">
                  <li>Revoke your sign-in access to Local Food Waste Minimizer</li>
                  <li>Cancel active surplus reservations and pending pickup claim codes</li>
                  <li>Deactivate active marketplace listings or donation offers</li>
                </ul>
              </div>

              <form onSubmit={handleConfirmDelete} className="space-y-4">
                <PasswordInput
                  label="Type Password to Confirm"
                  value={deletePassword}
                  onChange={(e) => setDeletePassword(e.target.value)}
                  placeholder="Enter your current password"
                  required
                />

                <div className="flex gap-3 justify-end pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowDeleteConfirmModal(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="destructive"
                    loading={deactivateAccountMutation.isPending}
                  >
                    Permanently Delete Account
                  </Button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Help & Platform User Guide Modal */}
      <AnimatePresence>
        {showHelpModal && (
          <div className="fixed inset-0 z-[10000] flex items-start justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-2xl m-auto bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-2xl overflow-hidden"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-indigo-100 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                    <BookOpen className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 dark:text-slate-100 text-lg">Platform User Guide & Support</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Everything you need to know about rescuing surplus food</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowHelpModal(false)}
                  className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  ✕
                </button>
              </div>

              {/* Navigation Tabs */}
              <div className="flex border-b border-slate-200 dark:border-slate-800 px-6 gap-4 text-xs font-semibold overflow-x-auto">
                {[
                  { id: 'getting-started', label: '🚀 Getting Started' },
                  { id: 'rescuing-food', label: '🥖 Rescuing Food' },
                  { id: 'vendor-guide', label: '🏬 Vendor Guide' },
                  { id: 'ngo-rescue', label: '🤝 NGO Rescue' },
                  { id: 'faq', label: '❓ FAQ & Support' },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setHelpTab(t.id)}
                    className={cn(
                      "py-3 border-b-2 transition-colors whitespace-nowrap",
                      helpTab === t.id
                        ? "border-emerald-600 text-emerald-600 dark:text-emerald-400"
                        : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                    )}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              {/* Content Panels */}
              <div className="p-6 text-xs leading-relaxed text-slate-600 dark:text-slate-300 max-h-[60vh] overflow-y-auto space-y-4">
                {helpTab === 'getting-started' && (
                  <div className="space-y-4">
                    <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Welcome to Local Food Waste Minimizer!</h4>
                    <p>
                      Our platform connects local food businesses (bakeries, restaurants, supermarkets) having surplus inventory with nearby customers and NGOs prior to item expiration.
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                      <div className="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/60 space-y-1">
                        <div className="font-bold text-emerald-800 dark:text-emerald-300 flex items-center gap-1.5">
                          <ShoppingBag className="w-3.5 h-3.5" /> For Customers
                        </div>
                        <p className="text-[11px] text-emerald-700 dark:text-emerald-400">
                          Discover 50–70% discounted fresh meals, bakery surplus, and groceries nearby. Reserve & claim in-store using your 6-digit claim code.
                        </p>
                      </div>
                      <div className="p-3.5 rounded-2xl bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800/60 space-y-1">
                        <div className="font-bold text-indigo-800 dark:text-indigo-300 flex items-center gap-1.5">
                          <Store className="w-3.5 h-3.5" /> For Food Vendors
                        </div>
                        <p className="text-[11px] text-indigo-700 dark:text-indigo-400">
                          Track inventory batches, publish discounted listings automatically, track revenue recovery, and divert food waste.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {helpTab === 'rescuing-food' && (
                  <div className="space-y-3">
                    <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">How to Order & Claim Surplus Food</h4>
                    <ol className="list-decimal pl-5 space-y-2">
                      <li><strong>Browse Marketplace:</strong> Use filters (Category, Map View) to explore surplus items nearby.</li>
                      <li><strong>Reserve & Checkout:</strong> Select item quantity and click <em>Reserve Now</em>.</li>
                      <li><strong>Receive Claim Code:</strong> You will receive a unique 6-digit claim code (e.g. <code>#MKT-1234</code>).</li>
                      <li><strong>In-Store Pickup:</strong> Present your claim code at the store before expiration to pick up your order!</li>
                    </ol>
                  </div>
                )}

                {helpTab === 'vendor-guide' && (
                  <div className="space-y-3">
                    <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Vendor Inventory & Listing Guide</h4>
                    <ul className="list-disc pl-5 space-y-2">
                      <li><strong>Batch Management:</strong> Manage product stock, expiration dates, and branch inventories in real-time.</li>
                      <li><strong>AI Pricing Strategy:</strong> Utilize dynamic markdown calculations or manual pricing for optimal surplus sales.</li>
                      <li><strong>Claim Verification:</strong> Quickly verify customer claim codes at the counter from the <em>Vendor Orders</em> page.</li>
                    </ul>
                  </div>
                )}

                {helpTab === 'ngo-rescue' && (
                  <div className="space-y-3">
                    <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">NGO Direct Food Rescue</h4>
                    <p>
                      Registered non-profits and charities get access to free donation listings flagged by vendors for direct food rescue prior to expiration.
                    </p>
                  </div>
                )}

                {helpTab === 'faq' && (
                  <div className="space-y-3">
                    <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Frequently Asked Questions</h4>
                    <div className="space-y-2">
                      <p className="font-semibold text-slate-800 dark:text-slate-200">Q: What happens if an order is not picked up before expiration?</p>
                      <p className="text-slate-500 dark:text-slate-400">A: Unclaimed orders expire automatically and stock is updated accordingly.</p>
                      <p className="font-semibold text-slate-800 dark:text-slate-200 pt-2">Q: Need urgent assistance or support?</p>
                      <p className="text-emerald-600 dark:text-emerald-400 font-mono">Contact Support: support@foodwaste.org | +1 (800) 555-FOOD</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex justify-end">
                <Button variant="primary" size="sm" onClick={() => setShowHelpModal(false)}>
                  Got it, Close Guide
                </Button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
      </>,
      document.body
    )}
    </>
  );
};
