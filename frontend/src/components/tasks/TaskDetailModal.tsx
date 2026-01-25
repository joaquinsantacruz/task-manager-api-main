import { Modal } from '../common';
import { TaskOwnerEditor, TaskDueDateEditor, TaskStatusButtons } from './';
import { CommentForm, CommentList } from '../comments';
import { Task, TaskStatus } from '../../types';
import { useAuth } from '../../context/AuthContext';
import { useTaskOwnerEditor } from '../../hooks/useTaskOwnerEditor';
import { useTaskDueDateEditor } from '../../hooks/useTaskDueDateEditor';
import { useComments } from '../../hooks/useComments';

interface TaskDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: Task | null;
  onChangeStatus?: (taskId: number, newStatus: TaskStatus) => void;
  onChangeOwner?: (taskId: number, newOwnerId: number) => void;
  onChangeDueDate?: (taskId: number, newDueDate: string | null) => void;
}

export default function TaskDetailModal({ isOpen, onClose, task, onChangeStatus, onChangeOwner, onChangeDueDate }: TaskDetailModalProps) {
  const { user: authUser } = useAuth();
  const ownerEditor = useTaskOwnerEditor(task?.owner_id || null);
  const dueDateEditor = useTaskDueDateEditor(task?.due_date);
  const { comments, loading: commentsLoading, createComment, updateComment, deleteComment } = useComments(task?.id || null, isOpen);
  
  if (!task) return null;

  const isOwnerRole = authUser?.user?.role === 'owner';
  const currentUserId = authUser?.user?.id || 0;

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

  const handleSaveDueDate = () => {
    if (onChangeDueDate) {
      dueDateEditor.saveDueDate((newDueDate) => {
        onChangeDueDate(task.id, newDueDate);
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

        <TaskDueDateEditor
          dueDate={task.due_date}
          isOwnerRole={isOwnerRole}
          isEditing={dueDateEditor.isEditing}
          selectedDate={dueDateEditor.selectedDate}
          onStartEdit={dueDateEditor.startEditing}
          onCancelEdit={dueDateEditor.cancelEditing}
          onSaveEdit={handleSaveDueDate}
          onDateChange={dueDateEditor.setSelectedDate}
        />

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

        <div style={{ borderTop: '2px solid #eee', paddingTop: '1.5rem' }}>
          <h3 style={{ marginTop: 0, marginBottom: '1rem', color: '#333' }}>Comentarios</h3>
          <CommentForm onSubmit={createComment} />
          <CommentList
            comments={comments}
            currentUserId={currentUserId}
            loading={commentsLoading}
            onUpdate={updateComment}
            onDelete={deleteComment}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #eee' }}>
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
