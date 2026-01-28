'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GlassCard, Button, Input, Select, Modal, LoadingPage } from '@/components/ui';
import { cn } from '@/lib/utils';
import { tasksApi } from '@/lib/api';
import { notifications, getNotificationPreferences } from '@/lib/notifications';
import type { Task, TaskCreate, TaskUpdate, TaskPriority, TaskCategory, RecurringFrequency } from '@/types';

const TASK_CATEGORIES = [
  { value: 'bills', label: 'Bills & Payments', emoji: '💳' },
  { value: 'savings', label: 'Savings', emoji: '💰' },
  { value: 'review', label: 'Review & Planning', emoji: '📊' },
  { value: 'investment', label: 'Investment', emoji: '📈' },
  { value: 'budget', label: 'Budget', emoji: '📋' },
  { value: 'other', label: 'Other', emoji: '📝' },
];

const PRIORITY_CONFIG = {
  high: { label: 'High', color: 'text-red-600 dark:text-red-400', bg: 'bg-red-100 dark:bg-red-900/30', emoji: '🔴' },
  medium: { label: 'Medium', color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-100 dark:bg-amber-900/30', emoji: '🟡' },
  low: { label: 'Low', color: 'text-green-600 dark:text-green-400', bg: 'bg-green-100 dark:bg-green-900/30', emoji: '🟢' },
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'dueDate' | 'priority' | 'created'>('dueDate');
  const [formLoading, setFormLoading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium' as TaskPriority,
    category: 'bills' as TaskCategory,
    due_date: '',
    is_recurring: false,
    recurring_frequency: 'monthly' as RecurringFrequency,
  });

  // Load tasks from API
  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      const data = await tasksApi.getAll();
      setTasks(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Check for overdue tasks and notify
  const checkOverdueTasks = useCallback(() => {
    const prefs = getNotificationPreferences();
    if (!prefs.enabled || !prefs.taskReminders) return;

    const overdueTasks = tasks.filter(
      (t) => !t.is_completed && t.due_date && new Date(t.due_date) < new Date(new Date().toDateString())
    );

    if (overdueTasks.length > 0) {
      const firstOverdue = overdueTasks[0];
      notifications.taskOverdue(firstOverdue.title);
    }
  }, [tasks]);

  // Check for overdue tasks on mount (once per session)
  useEffect(() => {
    const hasCheckedToday = sessionStorage.getItem('overdue_check_' + new Date().toDateString());
    if (!hasCheckedToday && tasks.length > 0) {
      const timer = setTimeout(() => {
        checkOverdueTasks();
        sessionStorage.setItem('overdue_check_' + new Date().toDateString(), 'true');
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [tasks.length, checkOverdueTasks]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) return;

    setFormLoading(true);
    try {
      if (editingTask) {
        // Update existing task
        const updateData: TaskUpdate = {
          title: formData.title,
          description: formData.description || undefined,
          priority: formData.priority,
          category: formData.category,
          due_date: formData.due_date || undefined,
          is_recurring: formData.is_recurring,
          recurring_frequency: formData.is_recurring ? formData.recurring_frequency : undefined,
        };
        const updated = await tasksApi.update(editingTask.id, updateData);
        setTasks((prev) => prev.map((t) => (t.id === editingTask.id ? updated : t)));
      } else {
        // Create new task
        const createData: TaskCreate = {
          title: formData.title,
          description: formData.description || undefined,
          priority: formData.priority,
          category: formData.category,
          due_date: formData.due_date || undefined,
          is_recurring: formData.is_recurring,
          recurring_frequency: formData.is_recurring ? formData.recurring_frequency : undefined,
        };
        const newTask = await tasksApi.create(createData);
        setTasks((prev) => [newTask, ...prev]);
      }

      resetForm();
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to save task:', err);
    } finally {
      setFormLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      priority: 'medium',
      category: 'bills',
      due_date: '',
      is_recurring: false,
      recurring_frequency: 'monthly',
    });
    setEditingTask(null);
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description || '',
      priority: task.priority,
      category: task.category,
      due_date: task.due_date || '',
      is_recurring: task.is_recurring,
      recurring_frequency: task.recurring_frequency || 'monthly',
    });
    setIsModalOpen(true);
  };

  const handleToggleComplete = async (taskId: string) => {
    try {
      const task = tasks.find((t) => t.id === taskId);
      if (!task) return;

      const updated = await tasksApi.toggleComplete(taskId);
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));

      // Send completion notification
      if (updated.is_completed) {
        const prefs = getNotificationPreferences();
        if (prefs.enabled && prefs.taskReminders) {
          notifications.taskCompleted(updated.title);
        }

        // If it was a recurring task, fetch tasks again to get the new occurrence
        if (task.is_recurring) {
          setTimeout(() => fetchTasks(), 500);
        }
      }
    } catch (err) {
      console.error('Failed to toggle task:', err);
    }
  };

  const handleDelete = async (taskId: string) => {
    try {
      await tasksApi.delete(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      console.error('Failed to delete task:', err);
    }
  };

  const getCategoryInfo = (categoryValue: string) => {
    return TASK_CATEGORIES.find((c) => c.value === categoryValue) || TASK_CATEGORIES[5];
  };

  const isOverdue = (dueDate?: string | null) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date(new Date().toDateString());
  };

  const isDueToday = (dueDate?: string | null) => {
    if (!dueDate) return false;
    const today = new Date().toDateString();
    return new Date(dueDate).toDateString() === today;
  };

  const isDueSoon = (dueDate?: string | null) => {
    if (!dueDate) return false;
    const due = new Date(dueDate);
    const today = new Date();
    const diffDays = Math.ceil((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diffDays > 0 && diffDays <= 3;
  };

  // Filter and sort tasks
  const filteredTasks = tasks
    .filter((t) => {
      if (filter === 'active') return !t.is_completed;
      if (filter === 'completed') return t.is_completed;
      return true;
    })
    .filter((t) => {
      if (!searchQuery) return true;
      return (
        t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    })
    .sort((a, b) => {
      if (sortBy === 'priority') {
        const order = { high: 0, medium: 1, low: 2 };
        return order[a.priority] - order[b.priority];
      }
      if (sortBy === 'dueDate') {
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
      }
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });

  const activeTasks = tasks.filter((t) => !t.is_completed);
  const completedTasks = tasks.filter((t) => t.is_completed);
  const overdueTasks = activeTasks.filter((t) => isOverdue(t.due_date));

  if (loading) return <LoadingPage />;

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <GlassCard className="p-8 text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <Button onClick={fetchTasks}>Try again</Button>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Financial Tasks</h1>
          <p className="text-gray-500 dark:text-gray-400">Manage your financial to-dos and reminders</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Task
        </Button>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <GlassCard className="p-4" hover>
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Tasks</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{tasks.length}</p>
          </GlassCard>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <GlassCard className="p-4" hover>
            <p className="text-sm text-gray-500 dark:text-gray-400">Active</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{activeTasks.length}</p>
          </GlassCard>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <GlassCard className="p-4" hover>
            <p className="text-sm text-gray-500 dark:text-gray-400">Completed</p>
            <p className="text-2xl font-bold text-emerald-600 dark:text-green-400">{completedTasks.length}</p>
          </GlassCard>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <GlassCard className="p-4" hover>
            <p className="text-sm text-gray-500 dark:text-gray-400">Overdue</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">{overdueTasks.length}</p>
          </GlassCard>
        </motion.div>
      </div>

      {/* Filters */}
      <GlassCard className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              }
            />
          </div>
          <div className="flex gap-2">
            {(['all', 'active', 'completed'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                  filter === f
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                )}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
          <Select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            options={[
              { value: 'dueDate', label: 'Sort by Due Date' },
              { value: 'priority', label: 'Sort by Priority' },
              { value: 'created', label: 'Sort by Created' },
            ]}
            className="w-44"
          />
        </div>
      </GlassCard>

      {/* Task List */}
      <GlassCard className="p-4">
        {filteredTasks.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <span className="text-4xl mb-4 block">📋</span>
            <p className="font-medium">No tasks found</p>
            <p className="text-sm">Create your first financial task to get started!</p>
          </div>
        ) : (
          <div className="space-y-2">
            <AnimatePresence>
              {filteredTasks.map((task, index) => {
                const category = getCategoryInfo(task.category);
                const priority = PRIORITY_CONFIG[task.priority];
                const overdue = !task.is_completed && isOverdue(task.due_date);
                const dueToday = !task.is_completed && isDueToday(task.due_date);
                const dueSoon = !task.is_completed && isDueSoon(task.due_date);

                return (
                  <motion.div
                    key={task.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -100 }}
                    transition={{ delay: index * 0.03 }}
                    className={cn(
                      'flex items-center gap-4 p-4 rounded-xl border transition-all',
                      task.is_completed
                        ? 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 opacity-60'
                        : overdue
                        ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                        : dueToday
                        ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800'
                        : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'
                    )}
                  >
                    {/* Checkbox */}
                    <button
                      onClick={() => handleToggleComplete(task.id)}
                      className={cn(
                        'w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all',
                        task.is_completed
                          ? 'bg-emerald-500 border-emerald-500 text-white'
                          : 'border-gray-300 dark:border-gray-600 hover:border-purple-500'
                      )}
                    >
                      {task.is_completed && (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </button>

                    {/* Category Icon */}
                    <span className="text-xl">{category.emoji}</span>

                    {/* Task Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className={cn(
                          'font-medium truncate',
                          task.is_completed ? 'line-through text-gray-400' : 'text-gray-900 dark:text-white'
                        )}>
                          {task.title}
                        </p>
                        {task.is_recurring && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">
                            🔄 {task.recurring_frequency}
                          </span>
                        )}
                      </div>
                      {task.description && (
                        <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{task.description}</p>
                      )}
                      <div className="flex items-center gap-2 mt-1">
                        <span className={cn('text-xs px-2 py-0.5 rounded-full', priority.bg, priority.color)}>
                          {priority.emoji} {priority.label}
                        </span>
                        {task.due_date && (
                          <span className={cn(
                            'text-xs',
                            overdue ? 'text-red-600 dark:text-red-400 font-medium' :
                            dueToday ? 'text-amber-600 dark:text-amber-400 font-medium' :
                            dueSoon ? 'text-blue-600 dark:text-blue-400' :
                            'text-gray-500'
                          )}>
                            {overdue ? '⚠️ Overdue: ' : dueToday ? '📅 Today: ' : dueSoon ? '⏰ Soon: ' : '📅 '}
                            {new Date(task.due_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-1">
                      <button
                        onClick={() => handleEdit(task)}
                        className="p-2 text-gray-400 hover:text-blue-500 transition-colors"
                        title="Edit"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDelete(task.id)}
                        className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                        title="Delete"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}
      </GlassCard>

      {/* Add/Edit Task Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          resetForm();
        }}
        title={editingTask ? 'Edit Task' : 'Add New Task'}
        size="md"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Task Title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="e.g., Pay electricity bill"
            required
          />

          <Input
            label="Description (optional)"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Add more details..."
          />

          <div className="grid grid-cols-2 gap-4">
            <Select
              label="Category"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value as TaskCategory })}
              options={TASK_CATEGORIES.map((c) => ({ value: c.value, label: `${c.emoji} ${c.label}` }))}
            />

            <Select
              label="Priority"
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value as TaskPriority })}
              options={[
                { value: 'high', label: '🔴 High' },
                { value: 'medium', label: '🟡 Medium' },
                { value: 'low', label: '🟢 Low' },
              ]}
            />
          </div>

          <Input
            label="Due Date (optional)"
            type="date"
            value={formData.due_date}
            onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
          />

          <div className="space-y-3 p-4 rounded-xl bg-gray-50 dark:bg-gray-800">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="recurring"
                checked={formData.is_recurring}
                onChange={(e) => setFormData({ ...formData, is_recurring: e.target.checked })}
                className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <label htmlFor="recurring" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                🔄 Recurring Task
              </label>
            </div>

            {formData.is_recurring && (
              <Select
                label="Repeat"
                value={formData.recurring_frequency}
                onChange={(e) => setFormData({ ...formData, recurring_frequency: e.target.value as RecurringFrequency })}
                options={[
                  { value: 'daily', label: 'Daily' },
                  { value: 'weekly', label: 'Weekly' },
                  { value: 'monthly', label: 'Monthly' },
                ]}
              />
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setIsModalOpen(false);
                resetForm();
              }}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button type="submit" className="flex-1" isLoading={formLoading}>
              {editingTask ? 'Update Task' : 'Add Task'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
