// Task types matching backend API

export type TaskPriority = 'high' | 'medium' | 'low';

export type TaskCategory = 'bills' | 'savings' | 'review' | 'investment' | 'budget' | 'other';

export type RecurringFrequency = 'daily' | 'weekly' | 'monthly';

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string | null;
  priority: TaskPriority;
  category: TaskCategory;
  due_date?: string | null;
  is_recurring: boolean;
  recurring_frequency?: RecurringFrequency | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  category?: TaskCategory;
  due_date?: string;
  is_recurring?: boolean;
  recurring_frequency?: RecurringFrequency;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  category?: TaskCategory;
  due_date?: string;
  is_recurring?: boolean;
  recurring_frequency?: RecurringFrequency;
  is_completed?: boolean;
}

export interface TaskSummary {
  total_tasks: number;
  active_tasks: number;
  completed_tasks: number;
  overdue_count: number;
  due_soon_count: number;
  overdue_tasks: Array<{
    id: string;
    title: string;
    due_date: string | null;
    priority: TaskPriority;
  }>;
  due_soon_tasks: Array<{
    id: string;
    title: string;
    due_date: string | null;
    priority: TaskPriority;
  }>;
}

export interface TaskFilters {
  completed?: boolean;
  priority?: TaskPriority;
  category?: TaskCategory;
  skip?: number;
  limit?: number;
}
