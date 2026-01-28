'use client';

import { useState, useEffect, useCallback } from 'react';
import { transactionsApi } from '@/lib/api';
import type { Transaction, TransactionCreate, TransactionFilters, TransactionUpdate } from '@/types';

export function useTransactions(initialFilters?: TransactionFilters) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<TransactionFilters>(initialFilters || {});

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await transactionsApi.getAll(filters);
      setTransactions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const createTransaction = async (data: TransactionCreate): Promise<Transaction | null> => {
    try {
      const newTransaction = await transactionsApi.create(data);
      setTransactions((prev) => [newTransaction, ...prev]);
      return newTransaction;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create transaction');
      return null;
    }
  };

  const updateTransaction = async (id: string, data: TransactionUpdate): Promise<Transaction | null> => {
    try {
      const updated = await transactionsApi.update(id, data);
      setTransactions((prev) => prev.map((t) => (t.id === id ? updated : t)));
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update transaction');
      return null;
    }
  };

  const deleteTransaction = async (id: string): Promise<boolean> => {
    try {
      await transactionsApi.delete(id);
      setTransactions((prev) => prev.filter((t) => t.id !== id));
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete transaction');
      return false;
    }
  };

  const searchTransactions = async (query: string): Promise<void> => {
    if (!query.trim()) {
      fetchTransactions();
      return;
    }
    setLoading(true);
    try {
      const data = await transactionsApi.search(query);
      setTransactions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  return {
    transactions,
    loading,
    error,
    filters,
    setFilters,
    refetch: fetchTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    searchTransactions,
  };
}
