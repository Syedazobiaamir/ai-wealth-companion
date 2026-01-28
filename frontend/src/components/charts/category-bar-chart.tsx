'use client';

import { CategorySummary } from '@/types';
import { formatCurrency, generateChartColor } from '@/lib/utils';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface CategoryBarChartProps {
  data: CategorySummary[];
  className?: string;
}

export function CategoryBarChart({ data, className }: CategoryBarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No category data available
      </div>
    );
  }

  const chartData = data.map((item, index) => ({
    name: `${item.category_emoji} ${item.category_name}`,
    amount: typeof item.total_amount === 'string' ? parseFloat(item.total_amount) : item.total_amount,
    count: item.transaction_count,
    color: generateChartColor(index),
  }));

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string; payload?: { count?: number } }>; label?: string }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="font-medium">{label}</p>
          <p className="text-primary font-bold">{formatCurrency(payload[0].value)}</p>
          <p className="text-sm text-gray-500">{payload[0].payload?.count ?? 0} transactions</p>
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
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 30 }}>
          <CartesianGrid
            strokeDasharray="3 3"
            vertical={false}
            className="stroke-gray-200 dark:stroke-gray-700"
          />
          <XAxis
            dataKey="name"
            axisLine={false}
            tickLine={false}
            angle={-45}
            textAnchor="end"
            height={60}
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
          <Bar
            dataKey="amount"
            fill="#8884d8"
            radius={[4, 4, 0, 0]}
          >
            {chartData.map((entry, index) => (
              <rect
                key={`bar-${index}`}
                fill={entry.color}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  );
}