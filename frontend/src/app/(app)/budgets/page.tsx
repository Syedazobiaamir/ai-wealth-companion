'use client';

import { useEffect, useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GlassCard, Button, Input, Select, Modal, LoadingPage } from '@/components/ui';
import { BudgetProgressChart } from '@/components/charts';
import { budgetsApi, categoriesApi } from '@/lib/api';
import { formatCurrency, getMonthName, cn } from '@/lib/utils';
import type { Budget, BudgetCreate, BudgetStatus, Category } from '@/types';

// Priority types
type Priority = 'high' | 'medium' | 'low';

interface BudgetPriority {
  budgetId: string;
  priority: Priority;
}

const PRIORITY_CONFIG: Record<Priority, { label: string; color: string; bgColor: string; order: number }> = {
  high: {
    label: 'High',
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-100 dark:bg-red-900/30 border-red-200 dark:border-red-800',
    order: 1
  },
  medium: {
    label: 'Medium',
    color: 'text-yellow-600 dark:text-yellow-400',
    bgColor: 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-800',
    order: 2
  },
  low: {
    label: 'Low',
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-100 dark:bg-green-900/30 border-green-200 dark:border-green-800',
    order: 3
  },
};

// LocalStorage helpers for priorities
const PRIORITIES_KEY = 'awc_budget_priorities';

function loadPriorities(): Record<string, Priority> {
  if (typeof window === 'undefined') return {};
  try {
    const stored = localStorage.getItem(PRIORITIES_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch {
    return {};
  }
}

function savePriorities(priorities: Record<string, Priority>) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(PRIORITIES_KEY, JSON.stringify(priorities));
}

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [budgetStatus, setBudgetStatus] = useState<BudgetStatus[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [priorities, setPriorities] = useState<Record<string, Priority>>({});
  const [sortBy, setSortBy] = useState<'priority' | 'amount' | 'name'>('priority');
  const [filterPriority, setFilterPriority] = useState<Priority | 'all'>('all');

  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();
  const [selectedMonth, setSelectedMonth] = useState(currentMonth);
  const [selectedYear, setSelectedYear] = useState(currentYear);

  // Form state
  const [formData, setFormData] = useState<Partial<BudgetCreate> & { priority?: Priority }>({
    month: currentMonth,
    year: currentYear,
    limit_amount: 0,
    priority: 'medium',
  });
  const [formLoading, setFormLoading] = useState(false);

  // Load priorities from localStorage
  useEffect(() => {
    setPriorities(loadPriorities());
  }, []);

  useEffect(() => {
    async function loadData() {
      try {
        const [budgetData, statusData, catData] = await Promise.all([
          budgetsApi.getAll(selectedMonth, selectedYear),
          budgetsApi.getStatus(selectedMonth, selectedYear),
          categoriesApi.getAll(),
        ]);
        setBudgets(budgetData);
        setBudgetStatus(statusData);
        setCategories(catData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load budgets');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [selectedMonth, selectedYear]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.category_id || !formData.limit_amount) return;

    setFormLoading(true);
    try {
      const { priority, ...budgetData } = formData;
      const newBudget = await budgetsApi.create({
        ...budgetData,
        month: selectedMonth,
        year: selectedYear,
      } as BudgetCreate);
      setBudgets((prev) => [...prev.filter((b) => b.category_id !== newBudget.category_id), newBudget]);

      // Save priority to localStorage
      if (priority) {
        const newPriorities = { ...priorities, [newBudget.id]: priority };
        setPriorities(newPriorities);
        savePriorities(newPriorities);
      }

      // Refresh status
      const statusData = await budgetsApi.getStatus(selectedMonth, selectedYear);
      setBudgetStatus(statusData);

      setIsModalOpen(false);
      setFormData({ month: currentMonth, year: currentYear, limit_amount: 0, priority: 'medium' });
    } catch (err) {
      console.error('Failed to create budget:', err);
    } finally {
      setFormLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await budgetsApi.delete(id);
      setBudgets((prev) => prev.filter((b) => b.id !== id));

      // Remove priority from localStorage
      const { [id]: _, ...remaining } = priorities;
      setPriorities(remaining);
      savePriorities(remaining);

      const statusData = await budgetsApi.getStatus(selectedMonth, selectedYear);
      setBudgetStatus(statusData);
    } catch (err) {
      console.error('Failed to delete budget:', err);
    }
  };

  const handlePriorityChange = (budgetId: string, newPriority: Priority) => {
    const newPriorities = { ...priorities, [budgetId]: newPriority };
    setPriorities(newPriorities);
    savePriorities(newPriorities);
  };

  const getCategoryInfo = (categoryId: string) => {
    const cat = categories.find((c) => c.id === categoryId);
    return cat ? { name: cat.name, emoji: cat.emoji } : { name: 'Unknown', emoji: '❓' };
  };

  // Filter and sort budgets
  const sortedBudgets = useMemo(() => {
    let filtered = [...budgets];

    // Apply priority filter
    if (filterPriority !== 'all') {
      filtered = filtered.filter(b => (priorities[b.id] || 'medium') === filterPriority);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'priority': {
          const priorityA = priorities[a.id] || 'medium';
          const priorityB = priorities[b.id] || 'medium';
          return PRIORITY_CONFIG[priorityA].order - PRIORITY_CONFIG[priorityB].order;
        }
        case 'amount':
          return b.limit_amount - a.limit_amount;
        case 'name': {
          const nameA = getCategoryInfo(a.category_id).name;
          const nameB = getCategoryInfo(b.category_id).name;
          return nameA.localeCompare(nameB);
        }
        default:
          return 0;
      }
    });

    return filtered;
  }, [budgets, priorities, sortBy, filterPriority, categories]);

  // Generate month options
  const monthOptions = Array.from({ length: 12 }, (_, i) => ({
    value: String(i + 1),
    label: getMonthName(i + 1),
  }));

  // Generate year options (current year -2 to +1)
  const yearOptions = Array.from({ length: 4 }, (_, i) => ({
    value: String(currentYear - 2 + i),
    label: String(currentYear - 2 + i),
  }));

  // Get unused categories for the form
  const usedCategoryIds = budgets.map((b) => b.category_id);
  const availableCategories = categories.filter((c) => !usedCategoryIds.includes(c.id));

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
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Budgets</h1>
          <p className="text-gray-500 dark:text-gray-400">Set and track your spending limits</p>
        </div>
        <div className="relative group">
          <Button onClick={() => setIsModalOpen(true)} disabled={availableCategories.length === 0}>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Budget
          </Button>
          {availableCategories.length === 0 && (
            <div className="absolute bottom-full mb-2 right-0 hidden group-hover:block">
              <div className="bg-gray-900 text-white text-xs rounded-lg py-2 px-3 whitespace-nowrap">
                {categories.length === 0 ? 'No categories available' : 'All categories have budgets for this month'}
              </div>
            </div>
          )}
        </div>
      </motion.div>

      {/* Period Selector */}
      <GlassCard className="p-4">
        <div className="flex flex-col sm:flex-row gap-4 items-center">
          <span className="text-sm text-gray-500 dark:text-gray-400">View budgets for:</span>
          <div className="flex gap-2">
            <Select
              value={String(selectedMonth)}
              onChange={(e) => setSelectedMonth(Number(e.target.value))}
              options={monthOptions}
              className="w-36"
            />
            <Select
              value={String(selectedYear)}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              options={yearOptions}
              className="w-28"
            />
          </div>
        </div>
      </GlassCard>

      {/* Budget Progress */}
      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold mb-4">
          Budget Progress - {getMonthName(selectedMonth)} {selectedYear}
        </h2>
        {budgetStatus.length > 0 ? (
          <BudgetProgressChart data={budgetStatus} />
        ) : (
          <div className="text-center py-8 text-gray-500">
            No budgets set for this period. Add your first budget!
          </div>
        )}
      </GlassCard>

      {/* Budget List */}
      <GlassCard className="p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
          <h2 className="text-lg font-semibold">Budget Details</h2>

          {budgets.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {/* Priority Filter */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Filter:</span>
                <select
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value as Priority | 'all')}
                  className="px-3 py-1.5 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="all">All Priorities</option>
                  <option value="high">🔴 High</option>
                  <option value="medium">🟡 Medium</option>
                  <option value="low">🟢 Low</option>
                </select>
              </div>

              {/* Sort */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Sort:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as 'priority' | 'amount' | 'name')}
                  className="px-3 py-1.5 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="priority">Priority</option>
                  <option value="amount">Amount</option>
                  <option value="name">Name</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {budgets.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No budgets configured</div>
        ) : sortedBudgets.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No budgets match the filter</div>
        ) : (
          <div className="space-y-4">
            <AnimatePresence mode="popLayout">
              {sortedBudgets.map((budget, index) => {
                const { name, emoji } = getCategoryInfo(budget.category_id);
                const priority = priorities[budget.id] || 'medium';
                const priorityConfig = PRIORITY_CONFIG[priority];
                const { name: catName } = getCategoryInfo(budget.category_id);
                const status = budgetStatus.find(s => s.category === catName);
                const percentage = status ? Math.round((Number(status.spent) / Number(status.limit)) * 100) : 0;

                return (
                  <motion.div
                    key={budget.id}
                    layout
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ delay: index * 0.05 }}
                    className={cn(
                      "p-4 rounded-xl border transition-all duration-200",
                      "bg-gray-50 dark:bg-gray-800/50",
                      priority === 'high' && "border-l-4 border-l-red-500",
                      priority === 'medium' && "border-l-4 border-l-yellow-500",
                      priority === 'low' && "border-l-4 border-l-green-500"
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1">
                        <span className="text-2xl">{emoji}</span>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <p className="font-medium text-gray-900 dark:text-white">{name}</p>
                            {/* Priority Badge */}
                            <span className={cn(
                              "px-2 py-0.5 text-xs font-medium rounded-full border",
                              priorityConfig.bgColor,
                              priorityConfig.color
                            )}>
                              {priorityConfig.label}
                            </span>
                            {/* Usage Warning Badge */}
                            {percentage >= 100 && (
                              <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800">
                                Exceeded
                              </span>
                            )}
                            {percentage >= 80 && percentage < 100 && (
                              <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800">
                                Warning
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-500">
                            Limit: {formatCurrency(budget.limit_amount)}
                            {status && (
                              <span className="ml-2">
                                • Used: {formatCurrency(Number(status.spent))} ({percentage}%)
                              </span>
                            )}
                          </p>

                          {/* Progress Bar */}
                          {status && (
                            <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${Math.min(percentage, 100)}%` }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                className={cn(
                                  "h-full rounded-full",
                                  percentage >= 100 ? "bg-red-500" :
                                  percentage >= 80 ? "bg-amber-500" :
                                  "bg-gradient-to-r from-purple-500 to-blue-500"
                                )}
                              />
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 ml-4">
                        {/* Priority Selector */}
                        <select
                          value={priority}
                          onChange={(e) => handlePriorityChange(budget.id, e.target.value as Priority)}
                          className="px-2 py-1 text-xs rounded-lg bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                          <option value="high">🔴 High</option>
                          <option value="medium">🟡 Medium</option>
                          <option value="low">🟢 Low</option>
                        </select>

                        <button
                          onClick={() => handleDelete(budget.id)}
                          className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}

        {/* Priority Legend */}
        {budgets.length > 0 && (
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500 mb-2">Priority Legend:</p>
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-500"></span>
                <span className="text-sm text-gray-600 dark:text-gray-400">High - Essential spending</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                <span className="text-sm text-gray-600 dark:text-gray-400">Medium - Important</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-green-500"></span>
                <span className="text-sm text-gray-600 dark:text-gray-400">Low - Can reduce</span>
              </div>
            </div>
          </div>
        )}
      </GlassCard>

      {/* Add Budget Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Budget" size="md">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Select
            label="Category"
            value={formData.category_id || ''}
            onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
            options={availableCategories.map((c) => ({ value: c.id, label: `${c.emoji} ${c.name}` }))}
            placeholder="Select category"
            required
          />

          <Input
            label="Monthly Limit"
            type="number"
            step="0.01"
            min="0"
            value={formData.limit_amount || ''}
            onChange={(e) => setFormData({ ...formData, limit_amount: parseFloat(e.target.value) || 0 })}
            required
          />

          {/* Priority Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Priority Level
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(['high', 'medium', 'low'] as Priority[]).map((priority) => {
                const config = PRIORITY_CONFIG[priority];
                const isSelected = formData.priority === priority;
                return (
                  <button
                    key={priority}
                    type="button"
                    onClick={() => setFormData({ ...formData, priority })}
                    className={cn(
                      "p-3 rounded-xl border-2 transition-all duration-200 text-center",
                      isSelected
                        ? cn(config.bgColor, "border-current", config.color)
                        : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                    )}
                  >
                    <div className="flex flex-col items-center gap-1">
                      <span className="text-lg">
                        {priority === 'high' ? '🔴' : priority === 'medium' ? '🟡' : '🟢'}
                      </span>
                      <span className={cn(
                        "text-sm font-medium",
                        isSelected ? config.color : "text-gray-600 dark:text-gray-400"
                      )}>
                        {config.label}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
            <p className="mt-2 text-xs text-gray-500">
              {formData.priority === 'high' && "Essential spending that cannot be reduced"}
              {formData.priority === 'medium' && "Important but can be adjusted if needed"}
              {formData.priority === 'low' && "Discretionary spending that can be reduced"}
            </p>
          </div>

          <div className="pt-2 text-sm text-gray-500">
            Setting budget for: <strong>{getMonthName(selectedMonth)} {selectedYear}</strong>
          </div>

          <div className="flex gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)} className="flex-1">
              Cancel
            </Button>
            <Button type="submit" isLoading={formLoading} className="flex-1">
              Create Budget
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
