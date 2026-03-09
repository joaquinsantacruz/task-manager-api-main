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
      <div className="flex flex-col gap-6">
        <div>
          <label className="block mb-1 text-xs font-bold text-gray-500 uppercase tracking-wider">
            TÍTULO
          </label>
          <p className="text-lg text-gray-900">{task.title}</p>
        </div>

        {task.description && (
          <div>
            <label className="block mb-1 text-xs font-bold text-gray-500 uppercase tracking-wider">
              DESCRIPCIÓN
            </label>
            <p className="text-gray-700 whitespace-pre-wrap leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-100">{task.description}</p>
          </div>
        )}

        <div>
          <label className="block mb-1 text-xs font-bold text-gray-500 uppercase tracking-wider">
            ESTADO
          </label>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium 
            ${task.status === 'done' ? 'bg-green-100 text-green-800' : 
              task.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' : 
              'bg-gray-100 text-gray-800'}`}>
            {statusLabels[task.status]}
          </span>
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

        <div className="border-t-2 border-gray-100 pt-6 mt-2">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Comentarios</h3>
          <CommentForm onSubmit={createComment} />
          <div className="mt-6">
            <CommentList
              comments={comments}
              currentUserId={currentUserId}
              loading={commentsLoading}
              onUpdate={updateComment}
              onDelete={deleteComment}
            />
          </div>
        </div>

        <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-100">
          <TaskStatusButtons currentStatus={task.status} onStatusChange={handleStatusChange} />

          <button
            onClick={onClose}
            className="btn-secondary"
          >
            Cerrar
          </button>
        </div>
      </div>
    </Modal>
  );
}
