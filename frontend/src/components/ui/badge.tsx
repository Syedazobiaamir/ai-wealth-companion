'use client';

import { cn } from '@/lib/utils';
import { HTMLAttributes, forwardRef } from 'react';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'income' | 'expense' | 'warning' | 'success' | 'outline';
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', children, ...props }, ref) => {
    const variants = {
      default: 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300',
      income: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
      expense: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
      warning: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
      success: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
      outline: 'bg-transparent border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300',
    };

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
          variants[variant],
          className
        )}
        {...props}
      >
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

export { Badge };
