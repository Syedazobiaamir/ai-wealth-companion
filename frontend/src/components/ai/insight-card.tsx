'use client';

import { cn } from '@/lib/utils';

interface InsightCardProps {
  id: string;
  type: string;
  severity: string;
  title: string;
  content: string;
  actionSuggestion?: string | null;
  onDismiss?: (id: string) => void;
}

const severityConfig = {
  alert: { bg: 'bg-red-50 dark:bg-red-950/30', border: 'border-red-200 dark:border-red-800', badge: 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300', icon: '🔴' },
  warning: { bg: 'bg-amber-50 dark:bg-amber-950/30', border: 'border-amber-200 dark:border-amber-800', badge: 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300', icon: '🟡' },
  suggestion: { bg: 'bg-blue-50 dark:bg-blue-950/30', border: 'border-blue-200 dark:border-blue-800', badge: 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300', icon: '💡' },
  info: { bg: 'bg-gray-50 dark:bg-gray-800/50', border: 'border-gray-200 dark:border-gray-700', badge: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300', icon: 'ℹ️' },
} as const;

export function InsightCard({ id, type, severity, title, content, actionSuggestion, onDismiss }: InsightCardProps) {
  const config = severityConfig[severity as keyof typeof severityConfig] || severityConfig.info;

  return (
    <div className={cn('rounded-xl border p-4 relative', config.bg, config.border)}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1.5">
            <span>{config.icon}</span>
            <span className={cn('text-xs px-2 py-0.5 rounded-full font-medium', config.badge)}>
              {severity}
            </span>
          </div>
          <h4 className="font-semibold text-sm text-gray-900 dark:text-white mb-1">{title}</h4>
          <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">{content}</p>
          {actionSuggestion && (
            <p className="mt-2 text-xs font-medium text-purple-700 dark:text-purple-300">
              {actionSuggestion}
            </p>
          )}
        </div>
        {onDismiss && (
          <button
            onClick={() => onDismiss(id)}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
