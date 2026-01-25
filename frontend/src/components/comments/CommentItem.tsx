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
    <div style={{
      padding: '1rem',
      border: '1px solid #e0e0e0',
      borderRadius: '8px',
      backgroundColor: '#f9f9f9',
      marginBottom: '0.75rem'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '0.5rem'
      }}>
        <div>
          <strong style={{ color: '#333' }}>
            {comment.author_email || 'Usuario desconocido'}
          </strong>
          <span style={{ color: '#666', fontSize: '0.85rem', marginLeft: '0.5rem' }}>
            {formatDate(comment.created_at)}
          </span>
          {comment.updated_at && comment.updated_at !== comment.created_at && (
            <span style={{ color: '#999', fontSize: '0.75rem', marginLeft: '0.5rem', fontStyle: 'italic' }}>
              (editado)
            </span>
          )}
        </div>
        
        {isAuthor && !isEditing && (
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => setIsEditing(true)}
              disabled={isLoading}
              style={{
                padding: '0.25rem 0.75rem',
                fontSize: '0.85rem',
                border: '1px solid #007bff',
                borderRadius: '4px',
                background: 'white',
                color: '#007bff',
                cursor: 'pointer'
              }}
            >
              Editar
            </button>
            <button
              onClick={handleDelete}
              disabled={isLoading}
              style={{
                padding: '0.25rem 0.75rem',
                fontSize: '0.85rem',
                border: '1px solid #dc3545',
                borderRadius: '4px',
                background: 'white',
                color: '#dc3545',
                cursor: 'pointer'
              }}
            >
              Eliminar
            </button>
          </div>
        )}
      </div>

      {isEditing ? (
        <div>
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            disabled={isLoading}
            style={{
              width: '100%',
              minHeight: '80px',
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '0.95rem',
              fontFamily: 'inherit',
              resize: 'vertical'
            }}
          />
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
            <button
              onClick={handleSave}
              disabled={isLoading}
              style={{
                padding: '0.5rem 1rem',
                border: 'none',
                borderRadius: '4px',
                background: '#28a745',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              {isLoading ? 'Guardando...' : 'Guardar'}
            </button>
            <button
              onClick={handleCancel}
              disabled={isLoading}
              style={{
                padding: '0.5rem 1rem',
                border: '1px solid #6c757d',
                borderRadius: '4px',
                background: 'white',
                color: '#6c757d',
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              Cancelar
            </button>
          </div>
        </div>
      ) : (
        <p style={{ 
          margin: 0, 
          color: '#333',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word'
        }}>
          {comment.content}
        </p>
      )}
    </div>
  );
}
