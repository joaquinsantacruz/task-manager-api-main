import { Task } from '../types';
import TaskItem from './TaskItem';

interface TaskListProps {
  tasks: Task[];
  onOpenDetail: (task: Task) => void;
  onToggleStatus: (task: Task, e: React.MouseEvent) => void;
  onDelete: (id: number) => void;
}

export default function TaskList({ tasks, onOpenDetail, onToggleStatus, onDelete }: TaskListProps) {
  return (
    <ul className="task-list">
      {tasks.map(task => (
        <TaskItem 
          key={task.id}
          task={task}
          onOpenDetail={onOpenDetail}
          onToggleStatus={onToggleStatus}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}
