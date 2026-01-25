import { Task } from '../../types';

interface TaskItemProps {
  task: Task;
  onOpenDetail: (task: Task) => void;
  onToggleStatus: (task: Task, e: React.MouseEvent) => void;
  onDelete: (id: number) => void;
}

const STATUS_COLORS = {
  done: { bg: '#28a745', text: '#fff', label: 'COMPLETADA' },
  in_progress: { bg: '#ffc107', text: '#000', label: 'EN PROGRESO' },
  todo: { bg: '#6c757d', text: '#fff', label: 'POR HACER' }
};

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
