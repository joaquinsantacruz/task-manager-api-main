import { useState, useMemo } from 'react';
import { Task, TaskStatus } from '../types';

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
