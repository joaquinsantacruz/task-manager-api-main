import { useState } from 'react';
import { Comment } from '../../types';

/**
 * CommentItem - Component for displaying a single comment
 * 
 */
interface CommentItemProps {
  comment: Comment;
  currentUserId: number;
  onUpdate: (commentId: number, content: string) => Promise<boolean>;
  onDelete: (commentId: number) => Promise<boolean>;
}

export default function CommentItem({ comment, currentUserId, onUpdate, onDelete }: CommentItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [isLoading, setIsLoading] = useState(false);

  const isAuthor = comment.author_id === currentUserId;

  const handleSave = async () => {
    if (editContent.trim() === '') {
      alert('El comentario no puede estar vacío');
      return;
    }

    if (editContent === comment.content) {
      setIsEditing(false);
      return;
    }

    setIsLoading(true);
    const success = await onUpdate(comment.id, editContent);
    setIsLoading(false);

    if (success) {
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditContent(comment.content);
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (!confirm('¿Estás seguro de eliminar este comentario?')) return;

    setIsLoading(true);
    await onDelete(comment.id);
    setIsLoading(false);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="p-4 border border-gray-100 rounded-xl bg-white shadow-sm mb-3 transition-shadow hover:shadow-md">
      <div className="flex justify-between items-start mb-3">
        <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2">
          <strong className="text-gray-900 font-medium">
            {comment.author_email || 'Usuario desconocido'}
          </strong>
          <span className="text-gray-400 text-xs">
            {formatDate(comment.created_at)}
          </span>
          {comment.updated_at && comment.updated_at !== comment.created_at && (
            <span className="text-gray-400 text-[0.65rem] italic ml-1">
              (editado)
            </span>
          )}
        </div>
        
        {isAuthor && !isEditing && (
          <div className="flex gap-2">
            <button
              onClick={() => setIsEditing(true)}
              disabled={isLoading}
              className="text-xs px-2 py-1 text-primary-600 bg-primary-50 hover:bg-primary-100 rounded transition-colors"
            >
              Editar
            </button>
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className="text-xs px-2 py-1 text-red-600 bg-red-50 hover:bg-red-100 rounded transition-colors"
            >
              Eliminar
            </button>
          </div>
        )}
      </div>

      {isEditing ? (
        <div className="mt-2 animate-fade-in">
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            disabled={isLoading}
            className="w-full min-h-[80px] p-3 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all resize-y outline-none"
          />
          <div className="flex justify-end gap-2 mt-2">
            <button
              onClick={handleCancel}
              disabled={isLoading}
              className="px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors cursor-pointer"
            >
              Cancelar
            </button>
            <button
              onClick={handleSave}
              disabled={isLoading}
              className="px-3 py-1.5 text-sm font-medium text-white bg-green-500 hover:bg-green-600 rounded-lg transition-colors cursor-pointer shadow-sm"
            >
              {isLoading ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </div>
      ) : (
        <p className="m-0 text-gray-700 text-sm whitespace-pre-wrap break-words leading-relaxed pl-1 border-l-2 border-transparent">
          {comment.content}
        </p>
      )}
    </div>
  );
}
