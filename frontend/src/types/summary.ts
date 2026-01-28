// Summary types - API returns numeric values as strings

export interface FinancialSummary {
  total_income: number | string;
  total_expense: number | string;
  net_balance: number | string;
  period_start: string;
  period_end: string;
}

export interface CategorySummary {
  category_id: string;
  category_name: string;
  category_emoji: string;
  total_amount: number | string;
  transaction_count: number;
  percentage_of_total: number | string;
}

export interface MonthlyTrend {
  month: number;
  year: number;
  total_income: number | string;
  total_expense: number | string;
  net: number | string;
}

export interface DashboardSummary {
  financial_summary: FinancialSummary;
  category_breakdown: CategorySummary[];
  monthly_trends: MonthlyTrend[] | null;
  budget_alerts: string[] | null;
}
