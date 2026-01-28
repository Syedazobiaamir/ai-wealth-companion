'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { GlassCard, Select, LoadingPage } from '@/components/ui';
import { SpendingPieChart, MonthlyTrendChart } from '@/components/charts';
import { summaryApi } from '@/lib/api';
import { formatCurrency, formatDateForInput, getFirstDayOfMonth, getLastDayOfMonth, getMonthName } from '@/lib/utils';
import type { CategorySummary, MonthlyTrend, FinancialSummary } from '@/types';

export default function AnalyticsPage() {
  const [categoryBreakdown, setCategoryBreakdown] = useState<CategorySummary[]>([]);
  const [monthlyTrends, setMonthlyTrends] = useState<MonthlyTrend[]>([]);
  const [financialSummary, setFinancialSummary] = useState<FinancialSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const currentYear = new Date().getFullYear();
  const [selectedYear, setSelectedYear] = useState(currentYear);
  const [selectedType, setSelectedType] = useState<'expense' | 'income'>('expense');

  // Generate year options
  const yearOptions = Array.from({ length: 5 }, (_, i) => ({
    value: String(currentYear - 4 + i),
    label: String(currentYear - 4 + i),
  }));

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const startDate = `${selectedYear}-01-01`;
        const endDate = `${selectedYear}-12-31`;

        const [categories, trends, summary] = await Promise.all([
          summaryApi.getCategories(startDate, endDate, selectedType),
          summaryApi.getTrends(selectedYear),
          summaryApi.getFinancial(startDate, endDate),
        ]);

        setCategoryBreakdown(categories);
        setMonthlyTrends(trends);
        setFinancialSummary(summary);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load analytics');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [selectedYear, selectedType]);

  // Calculate statistics
  const totalTransactions = categoryBreakdown.reduce((sum, c) => sum + c.transaction_count, 0);
  const avgTransactionAmount = totalTransactions > 0
    ? categoryBreakdown.reduce((sum, c) => sum + (typeof c.total_amount === 'string' ? parseFloat(c.total_amount) : c.total_amount), 0) / totalTransactions
    : 0;
  const topCategory = categoryBreakdown[0];

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
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
          <p className="text-gray-500 dark:text-gray-400">Deep insights into your finances</p>
        </div>
      </motion.div>

      {/* Filters */}
      <GlassCard className="p-4">
        <div className="flex flex-col sm:flex-row gap-4 items-center">
          <span className="text-sm text-gray-500 dark:text-gray-400">Analyze:</span>
          <div className="flex gap-2">
            <Select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value as 'expense' | 'income')}
              options={[
                { value: 'expense', label: 'Expenses' },
                { value: 'income', label: 'Income' },
              ]}
              className="w-32"
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

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <GlassCard className="p-6" hover>
          <p className="text-sm text-gray-500 dark:text-gray-400">Total {selectedType === 'expense' ? 'Spending' : 'Income'}</p>
          <p className={`text-2xl font-bold mt-1 ${selectedType === 'expense' ? 'text-expense' : 'text-income'}`}>
            {formatCurrency(
              selectedType === 'expense'
                ? financialSummary?.total_expense || 0
                : financialSummary?.total_income || 0
            )}
          </p>
        </GlassCard>

        <GlassCard className="p-6" hover>
          <p className="text-sm text-gray-500 dark:text-gray-400">Transactions</p>
          <p className="text-2xl font-bold mt-1 text-gray-900 dark:text-white">{totalTransactions}</p>
        </GlassCard>

        <GlassCard className="p-6" hover>
          <p className="text-sm text-gray-500 dark:text-gray-400">Avg per Transaction</p>
          <p className="text-2xl font-bold mt-1 text-gray-900 dark:text-white">
            {formatCurrency(avgTransactionAmount)}
          </p>
        </GlassCard>

        <GlassCard className="p-6" hover>
          <p className="text-sm text-gray-500 dark:text-gray-400">Top Category</p>
          <p className="text-2xl font-bold mt-1 text-gray-900 dark:text-white">
            {topCategory ? `${topCategory.category_emoji} ${topCategory.category_name}` : 'N/A'}
          </p>
        </GlassCard>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold mb-4">
            {selectedType === 'expense' ? 'Spending' : 'Income'} by Category
          </h2>
          <SpendingPieChart data={categoryBreakdown} />
        </GlassCard>

        {/* Monthly Trends */}
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold mb-4">Monthly Trends - {selectedYear}</h2>
          <MonthlyTrendChart data={monthlyTrends} />
        </GlassCard>
      </div>

      {/* Category Details Table */}
      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold mb-4">Category Details</h2>
        {categoryBreakdown.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No data available for this period</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Category</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Amount</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Transactions</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">% of Total</th>
                </tr>
              </thead>
              <tbody>
                {categoryBreakdown.map((category, index) => (
                  <motion.tr
                    key={category.category_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{category.category_emoji}</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {category.category_name}
                        </span>
                      </div>
                    </td>
                    <td className={`py-3 px-4 text-right font-medium ${
                      selectedType === 'expense' ? 'text-expense' : 'text-income'
                    }`}>
                      {formatCurrency(category.total_amount)}
                    </td>
                    <td className="py-3 px-4 text-right text-gray-600 dark:text-gray-400">
                      {category.transaction_count}
                    </td>
                    <td className="py-3 px-4 text-right text-gray-600 dark:text-gray-400">
                      {(typeof category.percentage_of_total === 'string' ? parseFloat(category.percentage_of_total) : category.percentage_of_total).toFixed(1)}%
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>
    </div>
  );
}
