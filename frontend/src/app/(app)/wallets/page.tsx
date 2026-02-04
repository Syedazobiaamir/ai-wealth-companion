'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GlassCard, Button, Input, Select, Modal, LoadingPage } from '@/components/ui';
import { walletsApi, type Wallet, type WalletCreate, type WalletUpdate } from '@/lib/api';
import { formatCurrency, cn } from '@/lib/utils';

const WALLET_TYPES = [
  { value: 'bank', label: 'Bank Account', icon: '🏦' },
  { value: 'cash', label: 'Cash', icon: '💵' },
  { value: 'credit', label: 'Credit Card', icon: '💳' },
  { value: 'savings', label: 'Savings', icon: '🐷' },
  { value: 'investment', label: 'Investment', icon: '📈' },
];

const WALLET_COLORS = [
  { value: '#9333ea', label: 'Purple' },
  { value: '#3b82f6', label: 'Blue' },
  { value: '#22c55e', label: 'Green' },
  { value: '#f59e0b', label: 'Orange' },
  { value: '#ef4444', label: 'Red' },
  { value: '#ec4899', label: 'Pink' },
  { value: '#14b8a6', label: 'Teal' },
  { value: '#6366f1', label: 'Indigo' },
];

export default function WalletsPage() {
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingWallet, setEditingWallet] = useState<Wallet | null>(null);
  const [totalBalance, setTotalBalance] = useState<{ total_balance: number; currency: string } | null>(null);

  // Form state
  const [formData, setFormData] = useState<Partial<WalletCreate> & { current_balance?: number }>({
    name: '',
    type: 'bank',
    currency: 'PKR',
    initial_balance: 0,
    color: '#9333ea',
  });
  const [formLoading, setFormLoading] = useState(false);

  useEffect(() => {
    loadWallets();
  }, []);

  const loadWallets = async () => {
    try {
      const [walletsData, balanceData] = await Promise.all([
        walletsApi.getAll(true),
        walletsApi.getTotalBalance(),
      ]);
      setWallets(walletsData);
      setTotalBalance(balanceData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load wallets');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.type) return;

    setFormLoading(true);
    try {
      if (editingWallet) {
        const { initial_balance, currency, ...updateFields } = formData;
        const updated = await walletsApi.update(editingWallet.id, updateFields as WalletUpdate);
        setWallets((prev) => prev.map((w) => (w.id === updated.id ? updated : w)));
      } else {
        const newWallet = await walletsApi.create(formData as WalletCreate);
        setWallets((prev) => [...prev, newWallet]);
      }
      closeModal();
      loadWallets(); // Refresh to get updated total balance
    } catch (err) {
      console.error('Failed to save wallet:', err);
    } finally {
      setFormLoading(false);
    }
  };

  const handleEdit = (wallet: Wallet) => {
    setEditingWallet(wallet);
    setFormData({
      name: wallet.name,
      type: wallet.type,
      color: wallet.color || '#9333ea',
      current_balance: Number(wallet.current_balance),
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this wallet?')) return;
    try {
      await walletsApi.delete(id);
      setWallets((prev) => prev.filter((w) => w.id !== id));
      loadWallets(); // Refresh to get updated total balance
    } catch (err) {
      console.error('Failed to delete wallet:', err);
    }
  };

  const handleSetDefault = async (id: string) => {
    try {
      const updated = await walletsApi.setDefault(id);
      setWallets((prev) =>
        prev.map((w) => ({
          ...w,
          is_default: w.id === updated.id,
        }))
      );
    } catch (err) {
      console.error('Failed to set default wallet:', err);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingWallet(null);
    setFormData({
      name: '',
      type: 'bank',
      currency: 'PKR',
      initial_balance: 0,
      color: '#9333ea',
    });
  };

  const getWalletIcon = (type: string) => {
    return WALLET_TYPES.find((t) => t.value === type)?.icon || '💰';
  };

  const getWalletTypeName = (type: string) => {
    return WALLET_TYPES.find((t) => t.value === type)?.label || type;
  };

  if (loading) return <LoadingPage />;

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <GlassCard className="p-8 text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="text-primary hover:underline">
            Try again
          </button>
        </GlassCard>
      </div>
    );
  }

  const activeWallets = wallets.filter((w) => w.is_active);
  const inactiveWallets = wallets.filter((w) => !w.is_active);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Wallets</h1>
          <p className="text-gray-500 dark:text-gray-400">Manage your accounts and track balances</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Wallet
        </Button>
      </motion.div>

      {/* Total Balance Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <GlassCard className="p-6" hover glow>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Balance</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                {totalBalance ? formatCurrency(totalBalance.total_balance, totalBalance.currency) : '---'}
              </p>
              <p className="text-sm text-gray-400 mt-1">{activeWallets.length} active wallet(s)</p>
            </div>
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
              <span className="text-3xl">💰</span>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Wallets Grid */}
      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Your Wallets</h2>
        {activeWallets.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No wallets yet. Add your first wallet to start tracking!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <AnimatePresence>
              {activeWallets.map((wallet, index) => (
                <motion.div
                  key={wallet.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ delay: index * 0.05 }}
                  className="relative overflow-hidden rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 p-5"
                >
                  {/* Default badge */}
                  {wallet.is_default && (
                    <div className="absolute top-3 right-3 px-2 py-1 rounded-full bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-400 text-xs font-medium">
                      Default
                    </div>
                  )}

                  {/* Header */}
                  <div className="flex items-center gap-3 mb-4">
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center"
                      style={{ backgroundColor: wallet.color ? `${wallet.color}20` : '#9333ea20' }}
                    >
                      <span className="text-2xl">{getWalletIcon(wallet.type)}</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">{wallet.name}</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{getWalletTypeName(wallet.type)}</p>
                    </div>
                  </div>

                  {/* Balance */}
                  <div className="mb-4">
                    <p className="text-sm text-gray-500 dark:text-gray-400">Current Balance</p>
                    <p
                      className={cn(
                        'text-2xl font-bold',
                        Number(wallet.current_balance) >= 0 ? 'text-emerald-600 dark:text-green-500' : 'text-red-500'
                      )}
                    >
                      {formatCurrency(wallet.current_balance, wallet.currency)}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    {!wallet.is_default && (
                      <button
                        onClick={() => handleSetDefault(wallet.id)}
                        className="flex-1 px-3 py-2 text-sm rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                      >
                        Set Default
                      </button>
                    )}
                    <button
                      onClick={() => handleEdit(wallet)}
                      className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                        />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleDelete(wallet.id)}
                      className="p-2 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </GlassCard>

      {/* Inactive Wallets */}
      {inactiveWallets.length > 0 && (
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-500 dark:text-gray-400">Inactive Wallets</h2>
          <div className="space-y-3">
            {inactiveWallets.map((wallet) => (
              <div
                key={wallet.id}
                className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 opacity-60"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getWalletIcon(wallet.type)}</span>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{wallet.name}</p>
                    <p className="text-sm text-gray-500">{formatCurrency(wallet.current_balance, wallet.currency)}</p>
                  </div>
                </div>
                <span className="px-2 py-1 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-500 text-xs">
                  Inactive
                </span>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Add/Edit Wallet Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editingWallet ? 'Edit Wallet' : 'Add New Wallet'}
        size="md"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Wallet Name"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Main Bank Account"
            required
          />

          <Select
            label="Wallet Type"
            value={formData.type || 'bank'}
            onChange={(e) => setFormData({ ...formData, type: e.target.value as WalletCreate['type'] })}
            options={WALLET_TYPES.map((t) => ({ value: t.value, label: `${t.icon} ${t.label}` }))}
          />

          {!editingWallet ? (
            <>
              <Select
                label="Currency"
                value={formData.currency || 'PKR'}
                onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                options={[
                  { value: 'PKR', label: 'PKR - Pakistani Rupee' },
                  { value: 'USD', label: 'USD - US Dollar' },
                  { value: 'EUR', label: 'EUR - Euro' },
                  { value: 'GBP', label: 'GBP - British Pound' },
                  { value: 'AED', label: 'AED - UAE Dirham' },
                  { value: 'SAR', label: 'SAR - Saudi Riyal' },
                ]}
              />

              <Input
                label="Initial Balance"
                type="number"
                step="0.01"
                value={formData.initial_balance || ''}
                onChange={(e) => setFormData({ ...formData, initial_balance: parseFloat(e.target.value) || 0 })}
                placeholder="0.00"
              />
            </>
          ) : (
            <Input
              label="Current Balance"
              type="number"
              step="0.01"
              value={formData.current_balance ?? ''}
              onChange={(e) => setFormData({ ...formData, current_balance: parseFloat(e.target.value) || 0 })}
              placeholder="0.00"
            />
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Color</label>
            <div className="flex flex-wrap gap-2">
              {WALLET_COLORS.map((color) => (
                <button
                  key={color.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, color: color.value })}
                  className={cn(
                    'w-10 h-10 rounded-lg transition-all',
                    formData.color === color.value ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : ''
                  )}
                  style={{ backgroundColor: color.value }}
                  title={color.label}
                />
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={closeModal} className="flex-1">
              Cancel
            </Button>
            <Button type="submit" isLoading={formLoading} className="flex-1">
              {editingWallet ? 'Update Wallet' : 'Create Wallet'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
