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
      <div className="text-center py-8 text-gray-500 animate-pulse font-medium text-sm">
        Cargando comentarios...
      </div>
    );
  }

  if (comments.length === 0) {
    return (
      <div className="text-center py-8 px-4 text-gray-400 italic bg-gray-50/50 rounded-xl border-2 border-dashed border-gray-200 mt-4 text-sm">
        No hay comentarios aún. ¡Sé el primero en comentar!
      </div>
    );
  }

  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-4 tracking-wide uppercase">
        Comentarios <span className="text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full ml-1">{comments.length}</span>
      </h4>
      <div className="space-y-3">
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
