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
  done: { bg: '#28a745', text: '#fff', label: 'COMPLETADA' },
  in_progress: { bg: '#ffc107', text: '#000', label: 'EN PROGRESO' },
  todo: { bg: '#6c757d', text: '#fff', label: 'POR HACER' }
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
    <li className="task-item">
      <div 
        onClick={() => onOpenDetail(task)}
        style={{
          flex: 1,
          minWidth: 0,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}
      >
        {/* Badge de status clickeable */}
        <span
          onClick={(e) => onToggleStatus(task, e)}
          style={{
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '0.75rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            backgroundColor: statusConfig.bg,
            color: statusConfig.text,
            minWidth: '90px',
            textAlign: 'center',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.opacity = '0.8';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.opacity = '1';
          }}
        >
          {statusConfig.label}
        </span>

        {/* Título y descripción */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div 
            className={task.status === 'done' ? 'completed' : ''}
            style={{
              fontSize: '1.1rem',
              textDecoration: task.status === 'done' ? 'line-through' : 'none',
              color: task.status === 'done' ? '#888' : 'inherit',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            {task.title}
          </div>
          {task.description && (
            <div style={{
              fontSize: '0.875rem',
              color: '#888',
              marginTop: '4px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              width: '100%'
            }}>
              {task.description}
            </div>
          )}
        </div>
      </div>
      
      <button 
        onClick={() => onDelete(task.id)} 
        className="btn-delete"
      >
        Eliminar
      </button>
    </li>
  );
}
