'use client';

import { cn } from '@/lib/utils';

interface HealthScoreProps {
  score: number;
  grade: string;
  components: {
    budget_adherence: { score: number; weight: number; detail: string };
    savings_rate: { score: number; weight: number; detail: string };
    spending_consistency: { score: number; weight: number; detail: string };
    goal_progress: { score: number; weight: number; detail: string };
  };
  recommendations: string[];
}

function getScoreColor(score: number): string {
  if (score >= 80) return 'text-emerald-500';
  if (score >= 60) return 'text-blue-500';
  if (score >= 40) return 'text-amber-500';
  return 'text-red-500';
}

function getScoreRing(score: number): string {
  if (score >= 80) return 'stroke-emerald-500';
  if (score >= 60) return 'stroke-blue-500';
  if (score >= 40) return 'stroke-amber-500';
  return 'stroke-red-500';
}

export function HealthScoreDisplay({ score, grade, components, recommendations }: HealthScoreProps) {
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-2xl border border-white/30 dark:border-gray-700/50 p-5">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Financial Health</h3>

      <div className="flex items-center gap-6">
        {/* Score ring */}
        <div className="relative w-24 h-24 flex-shrink-0">
          <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="none" strokeWidth="8" className="stroke-gray-200 dark:stroke-gray-700" />
            <circle
              cx="50" cy="50" r="40" fill="none" strokeWidth="8"
              className={cn(getScoreRing(score), 'transition-all duration-1000')}
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={cn('text-2xl font-bold', getScoreColor(score))}>{score}</span>
            <span className="text-[10px] text-gray-500 dark:text-gray-400">{grade}</span>
          </div>
        </div>

        {/* Components */}
        <div className="flex-1 space-y-2">
          {Object.entries(components).map(([key, comp]) => (
            <div key={key} className="flex items-center gap-2">
              <div className="flex-1">
                <div className="flex justify-between text-[10px] text-gray-500 dark:text-gray-400 mb-0.5">
                  <span className="capitalize">{key.replace('_', ' ')}</span>
                  <span>{comp.score}%</span>
                </div>
                <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={cn(
                      'h-full rounded-full transition-all duration-700',
                      comp.score >= 70 ? 'bg-emerald-500' : comp.score >= 40 ? 'bg-amber-500' : 'bg-red-500'
                    )}
                    style={{ width: `${comp.score}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
          {recommendations.map((rec, i) => (
            <p key={i} className="text-xs text-gray-600 dark:text-gray-400 mb-1 flex items-start gap-1.5">
              <span className="text-purple-500 mt-0.5">•</span>
              {rec}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
