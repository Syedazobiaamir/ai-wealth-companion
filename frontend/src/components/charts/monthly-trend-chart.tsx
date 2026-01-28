'use client';

import { MonthlyTrend } from '@/types';
import { CHART_COLORS } from '@/lib/constants';
import { formatCurrency, getMonthName } from '@/lib/utils';
import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface MonthlyTrendChartProps {
  data: MonthlyTrend[];
  className?: string;
}

export function MonthlyTrendChart({ data, className }: MonthlyTrendChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No trend data available
      </div>
    );
  }

  const chartData = data.map((item) => ({
    month: getMonthName(item.month).slice(0, 3),
    Income: typeof item.total_income === 'string' ? parseFloat(item.total_income) : item.total_income,
    Expense: typeof item.total_expense === 'string' ? parseFloat(item.total_expense) : item.total_expense,
    Net: typeof item.net === 'string' ? parseFloat(item.net) : item.net,
  }));

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="font-medium mb-2">{label}</p>
          {payload.map((item, index) => (
            <p key={index} style={{ color: item.color }} className="text-sm">
              {item.name}: {formatCurrency(item.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="incomeGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.income} stopOpacity={0.3} />
              <stop offset="95%" stopColor={CHART_COLORS.income} stopOpacity={0} />
            </linearGradient>
            <linearGradient id="expenseGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.expense} stopOpacity={0.3} />
              <stop offset="95%" stopColor={CHART_COLORS.expense} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            vertical={false}
            className="stroke-gray-200 dark:stroke-gray-700"
          />
          <XAxis
            dataKey="month"
            axisLine={false}
            tickLine={false}
            className="text-xs fill-gray-500"
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            className="text-xs fill-gray-500"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Area
            type="monotone"
            dataKey="Income"
            stroke={CHART_COLORS.income}
            strokeWidth={2}
            fill="url(#incomeGradient)"
          />
          <Area
            type="monotone"
            dataKey="Expense"
            stroke={CHART_COLORS.expense}
            strokeWidth={2}
            fill="url(#expenseGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
