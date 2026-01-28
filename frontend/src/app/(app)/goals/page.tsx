'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GlassCard, Button, Input, Select, Modal, LoadingPage } from '@/components/ui';
import { goalsApi } from '@/lib/api';
import { formatCurrency, cn } from '@/lib/utils';
import type { Goal, GoalCreate } from '@/lib/api';

const GOAL_EMOJIS = ['🎯', '🏠', '🚗', '✈️', '💰', '📱', '💻', '🎓', '💍', '🏥', '👶', '🎉'];
const GOAL_COLORS = [
  { value: 'purple', label: 'Purple', class: 'from-purple-500 to-purple-600' },
  { value: 'blue', label: 'Blue', class: 'from-blue-500 to-blue-600' },
  { value: 'green', label: 'Green', class: 'from-emerald-500 to-green-600' },
  { value: 'orange', label: 'Orange', class: 'from-orange-500 to-amber-600' },
  { value: 'pink', label: 'Pink', class: 'from-pink-500 to-rose-600' },
];

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAddProgressOpen, setIsAddProgressOpen] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [progressAmount, setProgressAmount] = useState<number>(0);

  // Form state
  const [formData, setFormData] = useState<Partial<GoalCreate>>({
    name: '',
    description: '',
    target_amount: 0,
    emoji: '🎯',
    color: 'purple',
    priority: 1,
  });
  const [formLoading, setFormLoading] = useState(false);

  useEffect(() => {
    loadGoals();
  }, []);

  const loadGoals = async () => {
    try {
      const data = await goalsApi.getAll();
      setGoals(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load goals');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.target_amount) return;

    setFormLoading(true);
    try {
      const newGoal = await goalsApi.create(formData as GoalCreate);
      setGoals((prev) => [...prev, newGoal]);
      setIsModalOpen(false);
      setFormData({
        name: '',
        description: '',
        target_amount: 0,
        emoji: '🎯',
        color: 'purple',
        priority: 1,
      });
    } catch (err) {
      console.error('Failed to create goal:', err);
    } finally {
      setFormLoading(false);
    }
  };

  const handleAddProgress = async () => {
    if (!selectedGoal || progressAmount <= 0) return;

    try {
      const updated = await goalsApi.addProgress(selectedGoal.id, progressAmount);
      setGoals((prev) => prev.map((g) => (g.id === updated.id ? updated : g)));
      setIsAddProgressOpen(false);
      setProgressAmount(0);
      setSelectedGoal(null);
    } catch (err) {
      console.error('Failed to add progress:', err);
    }
  };

  const handleMarkComplete = async (goal: Goal) => {
    try {
      const updated = await goalsApi.complete(goal.id);
      setGoals((prev) => prev.map((g) => (g.id === updated.id ? updated : g)));
    } catch (err) {
      console.error('Failed to complete goal:', err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await goalsApi.delete(id);
      setGoals((prev) => prev.filter((g) => g.id !== id));
    } catch (err) {
      console.error('Failed to delete goal:', err);
    }
  };

  const getProgressPercentage = (goal: Goal) => {
    return Math.min(100, (Number(goal.current_amount) / Number(goal.target_amount)) * 100);
  };

  const getColorClass = (color?: string) => {
    return GOAL_COLORS.find((c) => c.value === color)?.class || 'from-purple-500 to-purple-600';
  };

  if (loading) return <LoadingPage />;

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <GlassCard className="p-8 text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="text-primary hover:underline">
            Try again
          </button>
        </GlassCard>
      </div>
    );
  }

  const activeGoals = goals.filter((g) => g.status === 'active');
  const completedGoals = goals.filter((g) => g.status === 'completed');

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Financial Goals</h1>
          <p className="text-gray-500 dark:text-gray-400">Track your savings and achieve your dreams</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Goal
        </Button>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <GlassCard className="p-6" hover glow>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Active Goals</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">{activeGoals.length}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                <span className="text-2xl">🎯</span>
              </div>
            </div>
          </GlassCard>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <GlassCard className="p-6" hover glow>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Completed</p>
                <p className="text-3xl font-bold text-emerald-600 dark:text-green-500 mt-1">{completedGoals.length}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center">
                <span className="text-2xl">✅</span>
              </div>
            </div>
          </GlassCard>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <GlassCard className="p-6" hover glow>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Saved</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {formatCurrency(goals.reduce((sum, g) => sum + Number(g.current_amount), 0))}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
                <span className="text-2xl">💰</span>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>

      {/* Active Goals */}
      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Active Goals</h2>
        {activeGoals.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No active goals. Create your first savings goal!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <AnimatePresence>
              {activeGoals.map((goal, index) => {
                const progress = getProgressPercentage(goal);
                const colorClass = getColorClass(goal.color);
                return (
                  <motion.div
                    key={goal.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ delay: index * 0.05 }}
                    className="relative overflow-hidden rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 p-5"
                  >
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={cn('w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center', colorClass)}>
                          <span className="text-2xl">{goal.emoji}</span>
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white">{goal.name}</h3>
                          {goal.description && (
                            <p className="text-sm text-gray-500 dark:text-gray-400">{goal.description}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleMarkComplete(goal)}
                          className="p-2 text-gray-400 hover:text-emerald-500 transition-colors"
                          title="Mark as Complete"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDelete(goal.id)}
                          className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                          title="Delete"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>

                    {/* Progress */}
                    <div className="mb-4">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-500 dark:text-gray-400">Progress</span>
                        <span className="font-medium text-gray-900 dark:text-white">{progress.toFixed(0)}%</span>
                      </div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${progress}%` }}
                          transition={{ duration: 1, ease: 'easeOut' }}
                          className={cn('h-full rounded-full bg-gradient-to-r', colorClass)}
                        />
                      </div>
                    </div>

                    {/* Amount */}
                    <div className="flex justify-between items-center mb-4">
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Saved</p>
                        <p className="text-lg font-bold text-gray-900 dark:text-white">
                          {formatCurrency(goal.current_amount)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500 dark:text-gray-400">Target</p>
                        <p className="text-lg font-bold text-gray-900 dark:text-white">
                          {formatCurrency(goal.target_amount)}
                        </p>
                      </div>
                    </div>

                    {/* Add Progress Button */}
                    <Button
                      variant="secondary"
                      className="w-full"
                      onClick={() => {
                        setSelectedGoal(goal);
                        setIsAddProgressOpen(true);
                      }}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                      Add Progress
                    </Button>

                    {/* Target Date */}
                    {goal.target_date && (
                      <p className="text-xs text-gray-400 mt-3 text-center">
                        Target: {new Date(goal.target_date).toLocaleDateString()}
                      </p>
                    )}
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}
      </GlassCard>

      {/* Completed Goals */}
      {completedGoals.length > 0 && (
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <span>✅</span> Completed Goals
          </h2>
          <div className="space-y-3">
            {completedGoals.map((goal) => (
              <motion.div
                key={goal.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center justify-between p-4 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{goal.emoji}</span>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{goal.name}</p>
                    <p className="text-sm text-emerald-600 dark:text-emerald-400">
                      Achieved: {formatCurrency(goal.target_amount)}
                    </p>
                  </div>
                </div>
                <span className="text-2xl">🎉</span>
              </motion.div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Add Goal Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Goal" size="md">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Goal Name"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Emergency Fund, New Car"
            required
          />

          <Input
            label="Description (optional)"
            value={formData.description || ''}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="What are you saving for?"
          />

          <Input
            label="Target Amount"
            type="number"
            min="0"
            step="100"
            value={formData.target_amount || ''}
            onChange={(e) => setFormData({ ...formData, target_amount: parseFloat(e.target.value) || 0 })}
            required
          />

          <Input
            label="Target Date (optional)"
            type="date"
            value={formData.target_date || ''}
            onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Choose Icon
            </label>
            <div className="flex flex-wrap gap-2">
              {GOAL_EMOJIS.map((emoji) => (
                <button
                  key={emoji}
                  type="button"
                  onClick={() => setFormData({ ...formData, emoji })}
                  className={cn(
                    'w-10 h-10 rounded-lg text-xl flex items-center justify-center transition-all',
                    formData.emoji === emoji
                      ? 'bg-purple-100 dark:bg-purple-900 ring-2 ring-purple-500'
                      : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
                  )}
                >
                  {emoji}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Choose Color
            </label>
            <div className="flex gap-2">
              {GOAL_COLORS.map((color) => (
                <button
                  key={color.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, color: color.value })}
                  className={cn(
                    'w-10 h-10 rounded-lg bg-gradient-to-br transition-all',
                    color.class,
                    formData.color === color.value ? 'ring-2 ring-offset-2 ring-gray-400' : ''
                  )}
                />
              ))}
            </div>
          </div>

          <Select
            label="Priority"
            value={String(formData.priority || 1)}
            onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
            options={[
              { value: '1', label: '🔴 High Priority' },
              { value: '2', label: '🟡 Medium Priority' },
              { value: '3', label: '🟢 Low Priority' },
            ]}
          />

          <div className="flex gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)} className="flex-1">
              Cancel
            </Button>
            <Button type="submit" isLoading={formLoading} className="flex-1">
              Create Goal
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add Progress Modal */}
      <Modal
        isOpen={isAddProgressOpen}
        onClose={() => {
          setIsAddProgressOpen(false);
          setProgressAmount(0);
          setSelectedGoal(null);
        }}
        title={`Add Progress to "${selectedGoal?.name}"`}
        size="sm"
      >
        <div className="space-y-4">
          <Input
            label="Amount to Add"
            type="number"
            min="0"
            step="100"
            value={progressAmount || ''}
            onChange={(e) => setProgressAmount(parseFloat(e.target.value) || 0)}
            placeholder="Enter amount"
          />

          {selectedGoal && (
            <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Current:</span>
                <span className="font-medium">{formatCurrency(selectedGoal.current_amount)}</span>
              </div>
              <div className="flex justify-between text-sm mt-1">
                <span className="text-gray-500">After adding:</span>
                <span className="font-medium text-emerald-600">
                  {formatCurrency(Number(selectedGoal.current_amount) + progressAmount)}
                </span>
              </div>
              <div className="flex justify-between text-sm mt-1">
                <span className="text-gray-500">Remaining:</span>
                <span className="font-medium">
                  {formatCurrency(Math.max(0, Number(selectedGoal.target_amount) - Number(selectedGoal.current_amount) - progressAmount))}
                </span>
              </div>
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setIsAddProgressOpen(false);
                setProgressAmount(0);
              }}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button onClick={handleAddProgress} className="flex-1">
              Add Progress
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
