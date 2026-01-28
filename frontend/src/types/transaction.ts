// Transaction types

export type TransactionType = 'income' | 'expense';

export interface Transaction {
  id: string;
  type: TransactionType;
  amount: number | string;
  category_id: string;
  transaction_date: string; // ISO date string YYYY-MM-DD
  note: string | null;
  is_recurring: boolean;
  wallet_id?: string;
  tags?: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface TransactionWithCategory extends Transaction {
  category_name: string | null;
  category_emoji: string | null;
}

export interface TransactionCreate {
  type: TransactionType;
  amount: number;
  category_id: string;
  transaction_date: string;
  note?: string;
  is_recurring?: boolean;
  wallet_id?: string;
}

export interface TransactionUpdate {
  type?: TransactionType;
  amount?: number;
  category_id?: string;
  date?: string;
  note?: string;
  recurring?: boolean;
}

export interface TransactionFilters {
  start_date?: string;
  end_date?: string;
  type?: TransactionType;
  category_id?: string;
  sort_by?: string;
  sort_order?: string;
  skip?: number;
  limit?: number;
  [key: string]: string | number | undefined;
}
