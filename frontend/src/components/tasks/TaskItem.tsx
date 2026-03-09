import { Task } from '../../types';

/**
 * TaskItem Component Props
 */
interface TaskItemProps {
  /** The task object to display */
  task: Task;
  
  /** Callback when task is clicked to view details */
  onOpenDetail: (task: Task) => void;
  
  /** Callback when status badge is clicked to toggle status */
  onToggleStatus: (task: Task, e: React.MouseEvent) => void;
  
  /** Callback when delete button is clicked */
  onDelete: (id: number) => void;
}

/**
 * Status color configuration
 * Maps task status to visual styling (background, text color, label)
 */
const STATUS_COLORS = {
  done: { bg: 'bg-green-500', text: 'text-white', label: 'COMPLETADA' },
  in_progress: { bg: 'bg-yellow-400', text: 'text-yellow-900', label: 'EN PROGRESO' },
  todo: { bg: 'bg-gray-500', text: 'text-white', label: 'POR HACER' }
};

/**
 * TaskItem Component
 * 
 * Displays a single task in a list with interactive status badge and actions.
 * 
 * Features:
 *   - Clickable status badge to cycle through task statuses
 *   - Click on task to view full details
 *   - Visual distinction for completed tasks (strikethrough)
 *   - Truncated title and description with ellipsis
 *   - Delete button
 *   - Hover effects for interactive elements
 * 
 * Status Flow:
 *   - Clicking status badge cycles: TODO → IN_PROGRESS → DONE → TODO
 * 
 * @param task - Task object to display
 * @param onOpenDetail - Handler for clicking on task (opens detail modal)
 * @param onToggleStatus - Handler for clicking status badge (cycles status)
 * @param onDelete - Handler for delete button
 * 
 * @example
 * ```tsx
 * <TaskItem
 *   task={task}
 *   onOpenDetail={setSelectedTask}
 *   onToggleStatus={handleToggleStatus}
 *   onDelete={handleDeleteTask}
 * />
 * ```
 * 
 * Styling:
 *   - Status badge with color coding (green=done, yellow=in_progress, gray=todo)
 *   - Hover opacity effect on status badge
 *   - Strikethrough text for completed tasks
 *   - Ellipsis for long titles/descriptions
 */
export default function TaskItem({ task, onOpenDetail, onToggleStatus, onDelete }: TaskItemProps) {
  const statusConfig = STATUS_COLORS[task.status];

  return (
    <li className="group bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center gap-4 p-4">
        <div 
          onClick={() => onOpenDetail(task)}
          className="flex-1 min-w-0 cursor-pointer flex items-center gap-4"
        >
          {/* Badge de status clickeable */}
          <span
            onClick={(e) => onToggleStatus(task, e)}
            className={`px-3 py-1 text-xs font-bold rounded-full cursor-pointer text-center min-w-[100px] transition-opacity hover:opacity-80 ${statusConfig.bg} ${statusConfig.text}`}
          >
            {statusConfig.label}
          </span>

          {/* Título y descripción */}
          <div className="flex-1 min-w-0">
            <h3 
              className={`text-lg font-semibold truncate ${
                task.status === 'done' ? 'line-through text-gray-400' : 'text-gray-900'
              }`}
            >
              {task.title}
            </h3>
            {task.description && (
              <p className="mt-1 text-sm text-gray-500 truncate">
                {task.description}
              </p>
            )}
          </div>
        </div>
        
        <button 
          onClick={() => onDelete(task.id)} 
          className="opacity-0 group-hover:opacity-100 transition-opacity p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"
          title="Eliminar tarea"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
        </button>
      </div>
    </li>
  );
}
