import { useState, useMemo } from 'react';
import { Task, TaskStatus } from '../types';

/**
 * useTaskFilter - Custom hook for filtering tasks by status
 * 
 * This hook provides stateful filtering functionality for task lists,
 * allowing users to toggle visibility of tasks based on their status.
 * Uses memoization for efficient re-renders.
 * 
 * @param tasks - Array of tasks to filter
 * @returns Object containing:
 *   - selectedStatuses: Array of currently selected status filters
 *   - setSelectedStatuses: Function to update selected statuses
 *   - filteredTasks: Memoized array of tasks matching selected statuses
 * 
 * @example
 * ```tsx
 * const { filteredTasks, selectedStatuses, setSelectedStatuses } = useTaskFilter(allTasks);
 * // filteredTasks contains only tasks with statuses in selectedStatuses
 * ```
 * 
 * Performance:
 *   - Uses useMemo to prevent unnecessary filtering on every render
 *   - Only recalculates when tasks or selectedStatuses change
 */
export function useTaskFilter(tasks: Task[]) {
  const [selectedStatuses, setSelectedStatuses] = useState<TaskStatus[]>([
    'todo',
    'in_progress',
    'done'
  ]);

  const filteredTasks = useMemo(() => {
    return tasks.filter(task => selectedStatuses.includes(task.status));
  }, [tasks, selectedStatuses]);

  return {
    selectedStatuses,
    setSelectedStatuses,
    filteredTasks
  };
}
