// Budget types

export interface Budget {
  id: string;
  category_id: string;
  limit_amount: number;
  month: number;
  year: number;
  created_at?: string;
  updated_at?: string;
}

export interface BudgetCreate {
  category_id: string;
  limit_amount: number;
  month: number;
  year: number;
}

export interface BudgetUpdate {
  limit_amount?: number;
  month?: number;
  year?: number;
}

export interface BudgetStatus {
  category: string;
  emoji: string;
  limit: number | string;
  spent: number | string;
  remaining: number | string;
  percentage: number | string;
  exceeded: boolean;
  warning: boolean;
}

export interface BudgetAlerts {
  exceeded: BudgetStatus[];
  warnings: BudgetStatus[];
}
