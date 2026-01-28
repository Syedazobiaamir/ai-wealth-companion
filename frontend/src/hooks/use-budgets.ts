'use client';

import { useState, useEffect, useCallback } from 'react';
import { budgetsApi } from '@/lib/api';
import type { Budget, BudgetCreate, BudgetStatus, BudgetUpdate } from '@/types';

export function useBudgets(month?: number, year?: number) {
  const currentDate = new Date();
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [budgetStatus, setBudgetStatus] = useState<BudgetStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMonth, setSelectedMonth] = useState(month || currentDate.getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(year || currentDate.getFullYear());

  const fetchBudgets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [budgetData, statusData] = await Promise.all([
        budgetsApi.getAll(selectedMonth, selectedYear),
        budgetsApi.getStatus(selectedMonth, selectedYear),
      ]);
      setBudgets(budgetData);
      setBudgetStatus(statusData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch budgets');
    } finally {
      setLoading(false);
    }
  }, [selectedMonth, selectedYear]);

  useEffect(() => {
    fetchBudgets();
  }, [fetchBudgets]);

  const createBudget = async (data: BudgetCreate): Promise<Budget | null> => {
    try {
      const newBudget = await budgetsApi.create(data);
      await fetchBudgets(); // Refresh to get updated status
      return newBudget;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create budget');
      return null;
    }
  };

  const updateBudget = async (id: string, data: BudgetUpdate): Promise<Budget | null> => {
    try {
      const updated = await budgetsApi.update(id, data);
      await fetchBudgets();
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update budget');
      return null;
    }
  };

  const deleteBudget = async (id: string): Promise<boolean> => {
    try {
      await budgetsApi.delete(id);
      await fetchBudgets();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete budget');
      return false;
    }
  };

  return {
    budgets,
    budgetStatus,
    loading,
    error,
    selectedMonth,
    selectedYear,
    setSelectedMonth,
    setSelectedYear,
    refetch: fetchBudgets,
    createBudget,
    updateBudget,
    deleteBudget,
  };
}
