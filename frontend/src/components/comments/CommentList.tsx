import { Comment } from '../../types';
import { CommentItem } from './';

/**
 * CommentList - Component for displaying a list of comments
 * 
 */
interface CommentListProps {
  comments: Comment[];
  currentUserId: number;
  loading: boolean;
  onUpdate: (commentId: number, content: string) => Promise<boolean>;
  onDelete: (commentId: number) => Promise<boolean>;
}

export default function CommentList({ comments, currentUserId, loading, onUpdate, onDelete }: CommentListProps) {
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
        Cargando comentarios...
      </div>
    );
  }

  if (comments.length === 0) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '2rem', 
        color: '#999',
        fontStyle: 'italic',
        backgroundColor: '#f9f9f9',
        borderRadius: '8px',
        border: '1px dashed #ddd'
      }}>
        No hay comentarios aún. ¡Sé el primero en comentar!
      </div>
    );
  }

  return (
    <div style={{ marginTop: '1rem' }}>
      <h4 style={{ marginBottom: '1rem', color: '#333' }}>
        Comentarios ({comments.length})
      </h4>
      <div>
        {comments.map(comment => (
          <CommentItem
            key={comment.id}
            comment={comment}
            currentUserId={currentUserId}
            onUpdate={onUpdate}
            onDelete={onDelete}
          />
        ))}
      </div>
    </div>
  );
}
