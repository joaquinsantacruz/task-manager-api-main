import { TaskStatus } from '../types';

interface TaskStatusButtonsProps {
  currentStatus: TaskStatus;
  onStatusChange: (newStatus: TaskStatus) => void;
}

export default function TaskStatusButtons({ currentStatus, onStatusChange }: TaskStatusButtonsProps) {
  return (
    <div style={{ display: 'flex', gap: '0.5rem' }}>
      {currentStatus === 'todo' && (
        <button
          onClick={() => onStatusChange('in_progress')}
          style={{
            padding: '0.5rem 1rem',
            border: 'none',
            borderRadius: '4px',
            background: '#ffc107',
            color: '#000',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: 'bold'
          }}
        >
          En progreso &gt;
        </button>
      )}

      {currentStatus === 'in_progress' && (
        <>
          <button
            onClick={() => onStatusChange('todo')}
            style={{
              padding: '0.5rem 1rem',
              border: 'none',
              borderRadius: '4px',
              background: '#6c757d',
              color: 'white',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: 'bold'
            }}
          >
            &lt; Por hacer
          </button>
          <button
            onClick={() => onStatusChange('done')}
            style={{
              padding: '0.5rem 1rem',
              border: 'none',
              borderRadius: '4px',
              background: '#28a745',
              color: 'white',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: 'bold'
            }}
          >
            Completada &gt;
          </button>
        </>
      )}

      {currentStatus === 'done' && (
        <button
          onClick={() => onStatusChange('in_progress')}
          style={{
            padding: '0.5rem 1rem',
            border: 'none',
            borderRadius: '4px',
            background: '#ffc107',
            color: '#000',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: 'bold'
          }}
        >
          &lt; En progreso
        </button>
      )}
    </div>
  );
}
