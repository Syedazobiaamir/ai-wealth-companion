'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useTheme } from 'next-themes';
import { GlassCard, Button, Input, Select } from '@/components/ui';
import { useAuth } from '@/contexts/auth-context';
import { demoApi } from '@/lib/api';
import {
  notificationService,
  notifications as notificationFns,
  getNotificationPreferences,
  saveNotificationPreferences,
  type NotificationPreferences,
} from '@/lib/notifications';

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [seedingData, setSeedingData] = useState(false);
  const [resettingData, setResettingData] = useState(false);

  // Profile state - initialize from user context
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    currency: 'PKR',
    language: 'en',
  });

  // Update profile when user loads
  useEffect(() => {
    if (user) {
      setProfile({
        name: user.display_name || '',
        email: user.email,
        currency: user.preferred_currency || 'PKR',
        language: user.preferred_locale || 'en',
      });
    }
  }, [user]);

  // Browser notification state
  const [browserNotificationSupported, setBrowserNotificationSupported] = useState(false);
  const [browserNotificationPermission, setBrowserNotificationPermission] = useState<NotificationPermission>('default');
  const [notificationPrefs, setNotificationPrefs] = useState<NotificationPreferences>(getNotificationPreferences());
  const [testingNotification, setTestingNotification] = useState(false);

  // Check browser notification support
  useEffect(() => {
    setBrowserNotificationSupported(notificationService.isNotificationSupported());
    setBrowserNotificationPermission(notificationService.getPermission());
    setNotificationPrefs(getNotificationPreferences());
  }, []);

  // Request notification permission
  const handleEnableNotifications = async () => {
    const granted = await notificationService.requestPermission();
    setBrowserNotificationPermission(notificationService.getPermission());
    if (granted) {
      const newPrefs = { ...notificationPrefs, enabled: true };
      setNotificationPrefs(newPrefs);
      saveNotificationPreferences(newPrefs);
      // Show a test notification
      notificationFns.custom('Notifications Enabled', 'You will now receive financial alerts and reminders.');
    }
  };

  // Update notification preference
  const handleNotificationPrefChange = (key: keyof NotificationPreferences, value: boolean) => {
    const newPrefs = { ...notificationPrefs, [key]: value };
    setNotificationPrefs(newPrefs);
    saveNotificationPreferences(newPrefs);
  };

  // Test notification
  const handleTestNotification = async () => {
    setTestingNotification(true);
    await notificationFns.custom('Test Notification', 'Your browser notifications are working correctly!');
    setTimeout(() => setTestingNotification(false), 1000);
  };

  // Notification state (email/push - placeholder for future)
  const [notifications, setNotifications] = useState({
    budgetAlerts: true,
    weeklyReport: true,
    monthlyReport: true,
    tips: false,
  });

  const tabs = [
    { id: 'profile', label: 'Profile', icon: '👤' },
    { id: 'preferences', label: 'Preferences', icon: '⚙️' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'security', label: 'Security', icon: '🔒' },
    { id: 'data', label: 'Data & Privacy', icon: '📊' },
  ];

  const handleSaveProfile = () => {
    // Placeholder - would save to backend
    alert('Profile saved successfully!');
  };

  const handleSeedDemoData = async () => {
    if (!confirm('This will create demo transactions, budgets, and goals. Continue?')) return;
    setSeedingData(true);
    try {
      const result = await demoApi.seedData(6);
      alert(`Demo data created: ${result.data.transactions_created} transactions, ${result.data.budgets_created} budgets, ${result.data.goals_created} goals`);
      window.location.reload();
    } catch (err) {
      alert('Failed to seed demo data');
    } finally {
      setSeedingData(false);
    }
  };

  const handleResetData = async () => {
    if (!confirm('This will DELETE all your financial data. This cannot be undone. Continue?')) return;
    setResettingData(true);
    try {
      await demoApi.resetData();
      alert('All financial data has been reset');
      window.location.reload();
    } catch (err) {
      alert('Failed to reset data');
    } finally {
      setResettingData(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-gray-500 dark:text-gray-400">Manage your account preferences</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar Navigation */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-1"
        >
          <GlassCard className="p-2">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-purple-600 to-blue-500 text-white shadow-md'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  <span className="text-xl">{tab.icon}</span>
                  <span className="font-medium">{tab.label}</span>
                </button>
              ))}
            </nav>
          </GlassCard>
        </motion.div>

        {/* Content Area */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-3"
        >
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <GlassCard className="p-6">
              <h2 className="text-lg font-semibold mb-6">Profile Information</h2>

              {/* Avatar */}
              <div className="flex items-center gap-6 mb-8">
                <div className="w-20 h-20 rounded-full bg-gradient-to-r from-purple-600 to-blue-500 flex items-center justify-center text-white text-3xl font-bold">
                  {profile.name.charAt(0)}
                </div>
                <div>
                  <Button variant="secondary" size="sm">Change Photo</Button>
                  <p className="text-sm text-gray-500 mt-2">JPG, PNG or GIF. Max 2MB.</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Input
                  label="Full Name"
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                />
                <Input
                  label="Email Address"
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                />
                <Select
                  label="Currency"
                  value={profile.currency}
                  onChange={(e) => setProfile({ ...profile, currency: e.target.value })}
                  options={[
                    { value: 'PKR', label: 'Rs PKR - Pakistani Rupee' },
                    { value: 'USD', label: '$ USD - US Dollar' },
                    { value: 'EUR', label: '€ EUR - Euro' },
                    { value: 'GBP', label: '£ GBP - British Pound' },
                    { value: 'INR', label: '₹ INR - Indian Rupee' },
                    { value: 'AED', label: 'د.إ AED - UAE Dirham' },
                  ]}
                />
                <Select
                  label="Language"
                  value={profile.language}
                  onChange={(e) => setProfile({ ...profile, language: e.target.value })}
                  options={[
                    { value: 'en', label: 'English' },
                    { value: 'ur', label: 'اردو (Urdu)' },
                    { value: 'ar', label: 'العربية (Arabic)' },
                  ]}
                />
              </div>

              <div className="mt-8 flex justify-end">
                <Button onClick={handleSaveProfile}>Save Changes</Button>
              </div>
            </GlassCard>
          )}

          {/* Preferences Tab */}
          {activeTab === 'preferences' && (
            <GlassCard className="p-6">
              <h2 className="text-lg font-semibold mb-6">Appearance & Display</h2>

              {/* Theme Selection */}
              <div className="mb-8">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
                  Theme
                </label>
                <div className="grid grid-cols-3 gap-4">
                  {[
                    { id: 'light', label: 'Light', icon: '☀️' },
                    { id: 'dark', label: 'Dark', icon: '🌙' },
                    { id: 'system', label: 'System', icon: '💻' },
                  ].map((option) => (
                    <button
                      key={option.id}
                      onClick={() => setTheme(option.id)}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        theme === option.id
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-purple-300'
                      }`}
                    >
                      <span className="text-2xl block mb-2">{option.icon}</span>
                      <span className="text-sm font-medium">{option.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Dashboard Layout */}
              <div className="mb-8">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
                  Default Dashboard View
                </label>
                <Select
                  value="overview"
                  onChange={() => {}}
                  options={[
                    { value: 'overview', label: 'Overview (All sections)' },
                    { value: 'minimal', label: 'Minimal (Stats only)' },
                    { value: 'detailed', label: 'Detailed (With trends)' },
                  ]}
                />
              </div>

              {/* Date Format */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
                  Date Format
                </label>
                <Select
                  value="mdy"
                  onChange={() => {}}
                  options={[
                    { value: 'mdy', label: 'MM/DD/YYYY' },
                    { value: 'dmy', label: 'DD/MM/YYYY' },
                    { value: 'ymd', label: 'YYYY-MM-DD' },
                  ]}
                />
              </div>
            </GlassCard>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="space-y-6">
              {/* Browser Notifications Section */}
              <GlassCard className="p-6">
                <h2 className="text-lg font-semibold mb-6">🔔 Browser Notifications</h2>

                {!browserNotificationSupported ? (
                  <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
                    <p className="text-amber-700 dark:text-amber-300">
                      Your browser doesn&apos;t support notifications. Try using Chrome, Firefox, or Edge.
                    </p>
                  </div>
                ) : browserNotificationPermission === 'denied' ? (
                  <div className="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                    <h3 className="font-medium text-red-700 dark:text-red-400 mb-2">Notifications Blocked</h3>
                    <p className="text-sm text-red-600 dark:text-red-300">
                      You&apos;ve blocked notifications for this site. To enable them, click the lock icon in your browser&apos;s address bar and change the notification permission.
                    </p>
                  </div>
                ) : browserNotificationPermission !== 'granted' ? (
                  <div className="p-4 rounded-xl bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
                    <h3 className="font-medium text-purple-700 dark:text-purple-400 mb-2">Enable Notifications</h3>
                    <p className="text-sm text-purple-600 dark:text-purple-300 mb-4">
                      Get instant alerts for tasks, budgets, and goals directly in your browser.
                    </p>
                    <Button onClick={handleEnableNotifications}>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                      </svg>
                      Enable Browser Notifications
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* Status Banner */}
                    <div className="flex items-center justify-between p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">✅</span>
                        <div>
                          <h3 className="font-medium text-green-700 dark:text-green-400">Notifications Enabled</h3>
                          <p className="text-sm text-green-600 dark:text-green-300">
                            You&apos;ll receive alerts when important events occur
                          </p>
                        </div>
                      </div>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={handleTestNotification}
                        isLoading={testingNotification}
                      >
                        Test
                      </Button>
                    </div>

                    {/* Notification Type Settings */}
                    <div className="space-y-3">
                      {[
                        {
                          id: 'taskReminders',
                          title: 'Task Reminders',
                          description: 'Get notified about upcoming and overdue tasks',
                          icon: '✅',
                        },
                        {
                          id: 'budgetAlerts',
                          title: 'Budget Alerts',
                          description: 'Warnings when approaching or exceeding budget limits',
                          icon: '💰',
                        },
                        {
                          id: 'goalUpdates',
                          title: 'Goal Progress',
                          description: 'Celebrate milestones and goal completions',
                          icon: '🎯',
                        },
                        {
                          id: 'billReminders',
                          title: 'Bill Reminders',
                          description: 'Never miss a bill payment',
                          icon: '📅',
                        },
                      ].map((item) => (
                        <div
                          key={item.id}
                          className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50"
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-xl">{item.icon}</span>
                            <div>
                              <h3 className="font-medium text-gray-900 dark:text-white">{item.title}</h3>
                              <p className="text-sm text-gray-500">{item.description}</p>
                            </div>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={notificationPrefs[item.id as keyof NotificationPreferences] as boolean}
                              onChange={(e) =>
                                handleNotificationPrefChange(item.id as keyof NotificationPreferences, e.target.checked)
                              }
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-purple-600"></div>
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </GlassCard>

              {/* Email Notifications Section */}
              <GlassCard className="p-6">
                <h2 className="text-lg font-semibold mb-6">📧 Email Notifications</h2>
                <p className="text-sm text-gray-500 mb-4">
                  Configure email notifications for reports and summaries
                </p>

                <div className="space-y-4">
                  {[
                    {
                      id: 'budgetAlerts',
                      title: 'Budget Alerts',
                      description: 'Get notified when you exceed or approach your budget limits',
                    },
                    {
                      id: 'weeklyReport',
                      title: 'Weekly Summary',
                      description: 'Receive a weekly summary of your spending',
                    },
                    {
                      id: 'monthlyReport',
                      title: 'Monthly Report',
                      description: 'Detailed monthly financial report',
                    },
                    {
                      id: 'tips',
                      title: 'Financial Tips',
                      description: 'Personalized tips to help you save money',
                    },
                  ].map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50"
                    >
                      <div>
                        <h3 className="font-medium text-gray-900 dark:text-white">{item.title}</h3>
                        <p className="text-sm text-gray-500">{item.description}</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={notifications[item.id as keyof typeof notifications]}
                          onChange={(e) =>
                            setNotifications({ ...notifications, [item.id]: e.target.checked })
                          }
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-purple-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </GlassCard>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <GlassCard className="p-6">
              <h2 className="text-lg font-semibold mb-6">Security Settings</h2>

              {/* Change Password */}
              <div className="mb-8 p-6 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                <h3 className="font-medium text-gray-900 dark:text-white mb-4">Change Password</h3>
                <div className="space-y-4">
                  <Input label="Current Password" type="password" placeholder="••••••••" />
                  <Input label="New Password" type="password" placeholder="••••••••" />
                  <Input label="Confirm New Password" type="password" placeholder="••••••••" />
                  <Button>Update Password</Button>
                </div>
              </div>

              {/* Two-Factor Auth */}
              <div className="p-6 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">Two-Factor Authentication</h3>
                    <p className="text-sm text-gray-500">Add an extra layer of security to your account</p>
                  </div>
                  <Button variant="secondary">Enable 2FA</Button>
                </div>
              </div>

              {/* Sessions */}
              <div className="mt-6 p-6 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                <h3 className="font-medium text-gray-900 dark:text-white mb-4">Active Sessions</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">💻</span>
                      <div>
                        <p className="font-medium text-sm">Chrome on Windows</p>
                        <p className="text-xs text-gray-500">Current session</p>
                      </div>
                    </div>
                    <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">Active</span>
                  </div>
                </div>
              </div>
            </GlassCard>
          )}

          {/* Data & Privacy Tab */}
          {activeTab === 'data' && (
            <GlassCard className="p-6">
              <h2 className="text-lg font-semibold mb-6">Data & Privacy</h2>

              {/* Demo Data */}
              <div className="mb-6 p-6 rounded-xl bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
                <h3 className="font-medium text-purple-700 dark:text-purple-400 mb-2">Demo Data</h3>
                <p className="text-sm text-purple-600 dark:text-purple-300 mb-4">
                  Generate sample transactions, budgets, and goals to explore the app
                </p>
                <Button
                  onClick={handleSeedDemoData}
                  isLoading={seedingData}
                  variant="secondary"
                  className="bg-purple-500 text-white hover:bg-purple-600 border-purple-500"
                >
                  Generate Demo Data
                </Button>
              </div>

              {/* Export Data */}
              <div className="mb-6 p-6 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Export Your Data</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Download all your financial data in CSV or JSON format
                </p>
                <div className="flex gap-3">
                  <Button variant="secondary" size="sm">Export CSV</Button>
                  <Button variant="secondary" size="sm">Export JSON</Button>
                </div>
              </div>

              {/* Reset Data */}
              <div className="mb-6 p-6 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
                <h3 className="font-medium text-amber-700 dark:text-amber-400 mb-2">Reset Financial Data</h3>
                <p className="text-sm text-amber-600 dark:text-amber-300 mb-4">
                  Delete all transactions, budgets, wallets, and goals. Your account will remain.
                </p>
                <Button
                  onClick={handleResetData}
                  isLoading={resettingData}
                  variant="secondary"
                  className="bg-amber-500 text-white hover:bg-amber-600 border-amber-500"
                >
                  Reset All Data
                </Button>
              </div>

              {/* Delete Account */}
              <div className="p-6 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                <h3 className="font-medium text-red-700 dark:text-red-400 mb-2">Danger Zone</h3>
                <p className="text-sm text-red-600 dark:text-red-300 mb-4">
                  Once you delete your account, there is no going back. Please be certain.
                </p>
                <Button
                  variant="secondary"
                  className="bg-red-500 text-white hover:bg-red-600 border-red-500"
                >
                  Delete Account
                </Button>
              </div>
            </GlassCard>
          )}
        </motion.div>
      </div>
    </div>
  );
}
