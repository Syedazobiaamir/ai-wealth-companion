'use client';

import { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GlassCard, Button, Input, Select, Dropdown, Badge, Modal, LoadingPage } from '@/components/ui';
import { transactionsApi, categoriesApi, walletsApi, type Wallet } from '@/lib/api';
import { formatCurrency, formatDate, cn, debounce } from '@/lib/utils';
import type { Transaction, TransactionCreate, Category, TransactionType, TransactionFilters } from '@/types';

// Predefined tag suggestions for financial transactions
const SUGGESTED_TAGS = [
  'business', 'personal', 'recurring', 'subscription', 'one-time',
  'emergency', 'investment', 'savings', 'debt', 'loan',
  'groceries', 'utilities', 'rent', 'insurance', 'tax-deductible',
  'refund', 'gift', 'travel', 'medical', 'education'
];

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<Transaction | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('');
  const [filterTag, setFilterTag] = useState<string>('');

  // Tags input state
  const [tagInput, setTagInput] = useState('');
  const [showTagSuggestions, setShowTagSuggestions] = useState(false);
  const [formTags, setFormTags] = useState<string[]>([]);
  const tagInputRef = useRef<HTMLInputElement>(null);

  // Form state
  const [formData, setFormData] = useState<Partial<TransactionCreate>>({
    type: 'expense',
    amount: 0,
    transaction_date: new Date().toISOString().split('T')[0],
    note: '',
    is_recurring: false,
  });
  const [formLoading, setFormLoading] = useState(false);

  // Filter state
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('date');
  const [sortOrder, setSortOrder] = useState<string>('desc');

  // Extract all unique tags from transactions
  const allTags = useMemo(() => {
    const tagSet = new Set<string>();
    transactions.forEach(tx => {
      if (tx.tags && Array.isArray(tx.tags)) {
        tx.tags.forEach(tag => tagSet.add(tag));
      }
    });
    return Array.from(tagSet).sort();
  }, [transactions]);

  // Combined tag suggestions (predefined + existing)
  const tagSuggestions = useMemo(() => {
    const combined = new Set([...SUGGESTED_TAGS, ...allTags]);
    const filtered = Array.from(combined)
      .filter(tag =>
        tag.toLowerCase().includes(tagInput.toLowerCase()) &&
        !formTags.includes(tag)
      )
      .slice(0, 8);
    return filtered;
  }, [tagInput, formTags, allTags]);

  // Handle tag input
  const handleTagInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      addTag(tagInput.trim().toLowerCase());
    } else if (e.key === 'Backspace' && !tagInput && formTags.length > 0) {
      removeTag(formTags[formTags.length - 1]);
    } else if (e.key === 'Escape') {
      setShowTagSuggestions(false);
    }
  };

  const addTag = (tag: string) => {
    const normalizedTag = tag.toLowerCase().replace(/[^a-z0-9-]/g, '-');
    if (!formTags.includes(normalizedTag) && formTags.length < 5) {
      setFormTags([...formTags, normalizedTag]);
    }
    setTagInput('');
    setShowTagSuggestions(false);
  };

  const removeTag = (tag: string) => {
    setFormTags(formTags.filter(t => t !== tag));
  };

  const fetchTransactions = useCallback(async () => {
    try {
      const filters: TransactionFilters = {
        sort_by: sortBy,
        sort_order: sortOrder,
      };

      // Add type filter only if selected
      if (filterType) {
        filters.type = filterType as TransactionType;
      }

      // Add date range filters if both dates are provided
      if (startDate && endDate) {
        filters.start_date = startDate;
        filters.end_date = endDate;
      }

      console.log('Fetching with filters:', filters);
      const data = await transactionsApi.getAll(filters);
      console.log('Received transactions:', data);
      setTransactions(data);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load transactions');
    }
  }, [filterType, startDate, endDate, sortBy, sortOrder]);

  const searchTransactions = useCallback(
    debounce(async (query: string) => {
      if (!query.trim()) {
        fetchTransactions();
        return;
      }
      try {
        const data = await transactionsApi.search(query);
        setTransactions(data);
      } catch (err) {
        console.error('Search failed:', err);
      }
    }, 300),
    [fetchTransactions]
  );

  useEffect(() => {
    async function loadData() {
      try {
        const [catData, walletData] = await Promise.all([
          categoriesApi.getAll(),
          walletsApi.getAll(true).catch((err) => {
            console.error('Failed to load wallets:', err);
            return [];
          }),
        ]);
        setCategories(catData);
        setWallets(walletData);
        console.log('Loaded wallets:', walletData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  useEffect(() => {
    if (!loading) {
      fetchTransactions();
    }
  }, [filterType, startDate, endDate, sortBy, sortOrder, loading, fetchTransactions]);

  useEffect(() => {
    searchTransactions(searchQuery);
  }, [searchQuery, searchTransactions]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.category_id || !formData.amount) return;

    setFormLoading(true);
    try {
      const transactionData: TransactionCreate = {
        ...formData,
        tags: formTags.length > 0 ? formTags : undefined,
      } as TransactionCreate;

      if (editingTransaction) {
        // Update existing transaction
        const updatedTx = await transactionsApi.update(editingTransaction.id, transactionData);
        setTransactions((prev) => prev.map((t) => (t.id === updatedTx.id ? updatedTx : t)));
      } else {
        // Create new transaction
        const newTx = await transactionsApi.create(transactionData);
        setTransactions((prev) => [newTx, ...prev]);
      }

      closeModal();
    } catch (err) {
      console.error('Failed to save transaction:', err);
    } finally {
      setFormLoading(false);
    }
  };

  const handleEdit = (transaction: Transaction) => {
    setEditingTransaction(transaction);
    setFormData({
      type: transaction.type,
      amount: Number(transaction.amount),
      category_id: transaction.category_id,
      wallet_id: transaction.wallet_id,
      transaction_date: transaction.transaction_date,
      note: transaction.note || '',
      is_recurring: transaction.is_recurring,
    });
    setFormTags(transaction.tags && Array.isArray(transaction.tags) ? transaction.tags : []);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingTransaction(null);
    setFormData({
      type: 'expense',
      amount: 0,
      transaction_date: new Date().toISOString().split('T')[0],
      note: '',
      is_recurring: false,
    });
    setFormTags([]);
    setTagInput('');
  };

  // Filter transactions by tag
  const filteredTransactions = useMemo(() => {
    if (!filterTag) return transactions;
    return transactions.filter(tx =>
      tx.tags && Array.isArray(tx.tags) && tx.tags.includes(filterTag)
    );
  }, [transactions, filterTag]);

  const handleDelete = async (id: string) => {
    try {
      await transactionsApi.delete(id);
      setTransactions((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      console.error('Failed to delete transaction:', err);
    }
  };

  const getCategoryInfo = (categoryId: string) => {
    const cat = categories.find((c) => c.id === categoryId);
    return cat ? { name: cat.name, emoji: cat.emoji } : { name: 'Unknown', emoji: '❓' };
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

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Transactions</h1>
          <p className="text-gray-500 dark:text-gray-400">Manage your income and expenses</p>
        </div>
        <Button onClick={() => { setEditingTransaction(null); setIsModalOpen(true); }}>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Transaction
        </Button>
      </motion.div>

      {/* Filters */}
      <GlassCard className="p-4 !overflow-visible">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 overflow-visible">
          <div>
            <Input
              placeholder="Search transactions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              }
            />
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setFilterType('')}
              className={cn(
                'px-4 py-2 rounded-xl text-sm font-medium transition-all',
                filterType === ''
                  ? 'bg-purple-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
              )}
            >
              All
            </button>
            <button
              type="button"
              onClick={() => setFilterType('income')}
              className={cn(
                'px-4 py-2 rounded-xl text-sm font-medium transition-all',
                filterType === 'income'
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
              )}
            >
              💰 Income
            </button>
            <button
              type="button"
              onClick={() => setFilterType('expense')}
              className={cn(
                'px-4 py-2 rounded-xl text-sm font-medium transition-all',
                filterType === 'expense'
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
              )}
            >
              💸 Expense
            </button>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <Input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              placeholder="Start date"
              className="w-full"
            />
            <Input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              placeholder="End date"
              className="w-full"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <Select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              options={[
                { value: 'date', label: 'Date' },
                { value: 'amount', label: 'Amount' },
                { value: 'created_at', label: 'Created' },
              ]}
              className="w-full"
            />
            <Select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
              options={[
                { value: 'desc', label: 'Descending' },
                { value: 'asc', label: 'Ascending' },
              ]}
              className="w-full"
            />
          </div>
        </div>

        {/* Tag Filter */}
        {allTags.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm text-gray-500 dark:text-gray-400">Filter by tag:</span>
              <button
                onClick={() => setFilterTag('')}
                className={cn(
                  "px-3 py-1 text-xs rounded-full transition-colors",
                  !filterTag
                    ? "bg-purple-500 text-white"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
                )}
              >
                All
              </button>
              {allTags.map(tag => (
                <button
                  key={tag}
                  onClick={() => setFilterTag(tag)}
                  className={cn(
                    "px-3 py-1 text-xs rounded-full transition-colors",
                    filterTag === tag
                      ? "bg-purple-500 text-white"
                      : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
                  )}
                >
                  #{tag}
                </button>
              ))}
            </div>
          </div>
        )}
      </GlassCard>

      {/* Transactions List */}
      <GlassCard className="divide-y divide-gray-200 dark:divide-gray-700">
        <AnimatePresence mode="popLayout">
          {filteredTransactions.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              {filterTag ? `No transactions with tag #${filterTag}` : 'No transactions found. Add your first transaction!'}
            </div>
          ) : (
            filteredTransactions.map((tx, index) => {
              const { name, emoji } = getCategoryInfo(tx.category_id);
              const txTags = tx.tags && Array.isArray(tx.tags) ? tx.tags : [];
              return (
                <motion.div
                  key={tx.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ delay: index * 0.03 }}
                  className="flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                >
                  <div className="flex items-center gap-4 flex-1 min-w-0">
                    <div className="w-10 h-10 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-xl flex-shrink-0">
                      {emoji}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="font-medium text-gray-900 dark:text-white">{name}</p>
                        {tx.is_recurring && (
                          <span className="px-1.5 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
                            ↻ recurring
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                        {formatDate(tx.transaction_date)}
                        {tx.note && ` • ${tx.note}`}
                      </p>
                      {/* Tags */}
                      {txTags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {txTags.map(tag => (
                            <button
                              key={tag}
                              onClick={() => setFilterTag(tag)}
                              className="px-2 py-0.5 text-xs rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 hover:bg-purple-200 dark:hover:bg-purple-800/50 transition-colors"
                            >
                              #{tag}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <div className="text-right mr-2">
                      <p className={cn('font-semibold', tx.type === 'income' ? 'text-income' : 'text-expense')}>
                        {tx.type === 'income' ? '+' : '-'}{formatCurrency(tx.amount)}
                      </p>
                      <Badge variant={tx.type}>{tx.type}</Badge>
                    </div>
                    <button
                      onClick={() => handleEdit(tx)}
                      className="p-2 text-gray-400 hover:text-blue-500 transition-colors"
                      title="Edit"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleDelete(tx.id)}
                      className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                      title="Delete"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </GlassCard>

      {/* Add/Edit Transaction Modal */}
      <Modal isOpen={isModalOpen} onClose={closeModal} title={editingTransaction ? "Edit Transaction" : "Add Transaction"} size="md">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setFormData({ ...formData, type: 'expense' })}
              className={cn(
                'flex-1 py-3 rounded-xl font-medium transition-all',
                formData.type === 'expense'
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
              )}
            >
              Expense
            </button>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, type: 'income' })}
              className={cn(
                'flex-1 py-3 rounded-xl font-medium transition-all',
                formData.type === 'income'
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
              )}
            >
              Income
            </button>
          </div>

          <Input
            label="Amount"
            type="number"
            step="0.01"
            min="0"
            value={formData.amount || ''}
            onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
            required
          />

          <Select
            label="Category"
            value={formData.category_id || ''}
            onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
            options={categories.map((c) => ({ value: c.id, label: `${c.emoji} ${c.name}` }))}
            placeholder="Select category"
            required
          />

          {wallets.length > 0 ? (
            <Select
              label="Wallet"
              value={formData.wallet_id || ''}
              onChange={(e) => setFormData({ ...formData, wallet_id: e.target.value })}
              options={wallets.map((w) => ({ value: w.id, label: `${w.name} (${formatCurrency(w.current_balance, w.currency)})` }))}
              placeholder="Select wallet"
            />
          ) : (
            <div className="p-3 rounded-xl bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
              <p className="text-sm text-yellow-700 dark:text-yellow-400">
                No wallets found. <a href="/wallets" className="underline font-medium">Create a wallet first</a> to add transactions.
              </p>
            </div>
          )}

          <Input
            label="Date"
            type="date"
            value={formData.transaction_date || ''}
            onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
            required
          />

          <Input
            label="Note (optional)"
            value={formData.note || ''}
            onChange={(e) => setFormData({ ...formData, note: e.target.value })}
            placeholder="Add a note..."
          />

          {/* Tags Input */}
          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Tags (optional)
            </label>
            <div
              className={cn(
                "flex flex-wrap gap-2 p-2 rounded-xl border transition-colors min-h-[42px]",
                "bg-white dark:bg-gray-800",
                "border-gray-200 dark:border-gray-700",
                "focus-within:border-purple-500 focus-within:ring-2 focus-within:ring-purple-500/20"
              )}
              onClick={() => tagInputRef.current?.focus()}
            >
              {formTags.map(tag => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 px-2 py-1 text-sm bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-lg"
                >
                  #{tag}
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeTag(tag);
                    }}
                    className="hover:text-purple-900 dark:hover:text-purple-100"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </span>
              ))}
              <input
                ref={tagInputRef}
                type="text"
                value={tagInput}
                onChange={(e) => {
                  setTagInput(e.target.value);
                  setShowTagSuggestions(true);
                }}
                onKeyDown={handleTagInputKeyDown}
                onFocus={() => setShowTagSuggestions(true)}
                onBlur={() => setTimeout(() => setShowTagSuggestions(false), 200)}
                placeholder={formTags.length === 0 ? "Type and press Enter..." : formTags.length >= 5 ? "Max 5 tags" : ""}
                disabled={formTags.length >= 5}
                className="flex-1 min-w-[120px] bg-transparent outline-none text-sm placeholder:text-gray-400"
              />
            </div>

            {/* Tag Suggestions */}
            <AnimatePresence>
              {showTagSuggestions && tagSuggestions.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg overflow-hidden"
                >
                  {tagSuggestions.map(tag => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => addTag(tag)}
                      className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
                    >
                      <span className="text-purple-500">#</span>
                      <span className="text-gray-700 dark:text-gray-300">{tag}</span>
                      {SUGGESTED_TAGS.includes(tag) && (
                        <span className="ml-auto text-xs text-gray-400">suggested</span>
                      )}
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            <p className="mt-1 text-xs text-gray-500">
              Press Enter to add a tag. Max 5 tags per transaction.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="recurring"
              checked={formData.is_recurring || false}
              onChange={(e) => setFormData({ ...formData, is_recurring: e.target.checked })}
              className="rounded border-gray-300"
            />
            <label htmlFor="recurring" className="text-sm text-gray-600 dark:text-gray-400">
              Recurring transaction
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={closeModal} className="flex-1">
              Cancel
            </Button>
            <Button type="submit" isLoading={formLoading} className="flex-1">
              {editingTransaction ? 'Update Transaction' : 'Add Transaction'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
