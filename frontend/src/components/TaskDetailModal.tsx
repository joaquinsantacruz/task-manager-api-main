import Modal from './Modal';
import TaskOwnerEditor from './TaskOwnerEditor';
import TaskStatusButtons from './TaskStatusButtons';
import { Task, TaskStatus } from '../types';
import { useAuth } from '../context/AuthContext';
import { useTaskOwnerEditor } from '../hooks/useTaskOwnerEditor';

interface TaskDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: Task | null;
  onChangeStatus?: (taskId: number, newStatus: TaskStatus) => void;
  onChangeOwner?: (taskId: number, newOwnerId: number) => void;
}

export default function TaskDetailModal({ isOpen, onClose, task, onChangeStatus, onChangeOwner }: TaskDetailModalProps) {
  const { user: authUser } = useAuth();
  const ownerEditor = useTaskOwnerEditor(task?.owner_id || null);
  
  if (!task) return null;

  const isOwnerRole = authUser?.user?.role === 'owner';

  const statusLabels = {
    'todo': 'Por Hacer',
    'in_progress': 'En Progreso',
    'done': 'Completada'
  };

  const handleStatusChange = (newStatus: TaskStatus) => {
    if (onChangeStatus) {
      onChangeStatus(task.id, newStatus);
    }
  };

  const handleSaveOwner = () => {
    if (onChangeOwner) {
      ownerEditor.saveOwner((newOwnerId) => {
        onChangeOwner(task.id, newOwnerId);
      });
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Detalle de Tarea">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#666', fontSize: '0.875rem' }}>
            TÍTULO
          </label>
          <p style={{ margin: 0, fontSize: '1.1rem' }}>{task.title}</p>
        </div>

        {task.description && (
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#666', fontSize: '0.875rem' }}>
              DESCRIPCIÓN
            </label>
            <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{task.description}</p>
          </div>
        )}

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#666', fontSize: '0.875rem' }}>
            ESTADO
          </label>
          <p style={{ margin: 0 }}>{statusLabels[task.status]}</p>
        </div>

        <TaskOwnerEditor
          ownerEmail={task.owner_email || 'Sin asignar'}
          isOwnerRole={isOwnerRole}
          isEditing={ownerEditor.isEditing}
          users={ownerEditor.users}
          selectedOwnerId={ownerEditor.selectedOwnerId}
          currentOwnerId={task.owner_id}
          loadingUsers={ownerEditor.loadingUsers}
          onStartEdit={ownerEditor.startEditing}
          onCancelEdit={ownerEditor.cancelEditing}
          onSaveEdit={handleSaveOwner}
          onSelectOwner={ownerEditor.setSelectedOwnerId}
        />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
          <TaskStatusButtons currentStatus={task.status} onStatusChange={handleStatusChange} />

          <button
            onClick={onClose}
            style={{
              padding: '0.5rem 1.5rem',
              border: 'none',
              borderRadius: '4px',
              background: '#007bff',
              color: 'white',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Cerrar
          </button>
        </div>
      </div>
    </Modal>
  );
}
