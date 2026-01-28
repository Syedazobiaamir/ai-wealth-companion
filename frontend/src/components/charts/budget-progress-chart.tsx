'use client';

import { BudgetStatus } from '@/types';
import { cn, formatCurrency, formatPercentage } from '@/lib/utils';
import { motion } from 'framer-motion';

interface BudgetProgressChartProps {
  data: BudgetStatus[];
  className?: string;
}

export function BudgetProgressChart({ data, className }: BudgetProgressChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-500">
        No budget data available
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      {data.map((budget, index) => (
        <motion.div
          key={`${budget.category}-${index}`}
          className="space-y-2"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-lg">{budget.emoji}</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {budget.category}
              </span>
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {formatCurrency(budget.spent)} / {formatCurrency(budget.limit)}
            </div>
          </div>

          {/* Progress bar */}
          <div className="relative h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
            <motion.div
              className={cn(
                'absolute left-0 top-0 h-full rounded-full',
                budget.exceeded
                  ? 'bg-red-500'
                  : budget.warning
                  ? 'bg-amber-500'
                  : 'bg-green-500'
              )}
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(typeof budget.percentage === 'string' ? parseFloat(budget.percentage) : budget.percentage, 100)}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
            />
            {budget.exceeded && (
              <motion.div
                className="absolute left-0 top-0 h-full bg-red-600 rounded-full"
                initial={{ width: '100%' }}
                animate={{ width: `${Math.min(typeof budget.percentage === 'string' ? parseFloat(budget.percentage) : budget.percentage, 150)}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
                style={{ opacity: 0.3 }}
              />
            )}
          </div>

          <div className="flex items-center justify-between text-xs">
            <span
              className={cn(
                'font-medium',
                budget.exceeded
                  ? 'text-red-500'
                  : budget.warning
                  ? 'text-amber-500'
                  : 'text-green-500'
              )}
            >
              {formatPercentage(budget.percentage)}
              {budget.exceeded && ' (Over budget!)'}
              {budget.warning && !budget.exceeded && ' (Warning)'}
            </span>
            <span className="text-gray-500 dark:text-gray-400">
              {(typeof budget.remaining === 'string' ? parseFloat(budget.remaining) : budget.remaining) > 0
                ? `${formatCurrency(budget.remaining)} remaining`
                : `${formatCurrency(Math.abs(typeof budget.remaining === 'string' ? parseFloat(budget.remaining) : budget.remaining))} over`}
            </span>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
