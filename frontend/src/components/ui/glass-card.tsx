'use client';

import { cn } from '@/lib/utils';
import { motion, HTMLMotionProps } from 'framer-motion';
import { forwardRef } from 'react';

export interface GlassCardProps extends HTMLMotionProps<'div'> {
  variant?: 'default' | 'elevated' | 'subtle';
  hover?: boolean;
  glow?: boolean;
}

const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, variant = 'default', hover = false, glow = false, children, ...props }, ref) => {
    const variants = {
      default: 'bg-white/80 dark:bg-gray-900/70 border-gray-200/50 dark:border-gray-700/30',
      elevated: 'bg-white/90 dark:bg-gray-900/80 border-gray-200/60 dark:border-gray-600/30 shadow-xl',
      subtle: 'bg-white/60 dark:bg-gray-900/50 border-gray-200/30 dark:border-gray-800/30',
    };

    return (
      <motion.div
        ref={ref}
        className={cn(
          'rounded-2xl border border-white/20 dark:border-gray-700/30 shadow-glass relative',
          'before:absolute before:inset-0 before:rounded-2xl before:z-[-1]',
          'before:bg-gradient-to-br before:from-white/30 before:to-transparent',
          'dark:before:from-gray-800/30 dark:before:to-transparent',
          'bg-white/70 dark:bg-gray-900/70',
          'supports-[backdrop-filter]:bg-white/70 supports-[backdrop-filter]:dark:bg-gray-900/70',
          'supports-[backdrop-filter]:backdrop-blur-xl',
          variants[variant],
          hover && 'transition-all duration-200 hover:shadow-glass-hover hover:-translate-y-1 cursor-pointer',
          glow && 'hover:border-primary/30 hover:shadow-[0_0_30px_rgba(147,51,234,0.15)]',
          className
        )}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

GlassCard.displayName = 'GlassCard';

export { GlassCard };
