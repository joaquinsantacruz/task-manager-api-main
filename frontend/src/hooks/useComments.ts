import { useState, useCallback, useEffect } from 'react';
import { CommentService } from '../services/commentService';
import { Comment } from '../types';

/**
 * useComments - Custom hook for managing comments on a task
 * 
 * Following SOLID principles:
 * - Single Responsibility: Manages comment state and operations for a single task
 * - Dependency Inversion: Depends on CommentService abstraction
 * - Open/Closed: Easy to extend with new comment operations
 * 
 * @param taskId - The ID of the task to fetch comments for
 * @param autoFetch - Whether to automatically fetch comments on mount
 * @returns Comment state and CRUD operations
 */
export const useComments = (taskId: number | null, autoFetch: boolean = true) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch comments for the task
   */
  const fetchComments = useCallback(async () => {
    if (!taskId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await CommentService.getTaskComments(taskId);
      setComments(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar comentarios';
      setError(errorMessage);
      console.error('Error fetching comments:', err);
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  /**
   * Create a new comment
   */
  const createComment = useCallback(async (content: string): Promise<boolean> => {
    if (!taskId) return false;
    
    setLoading(true);
    setError(null);
    
    try {
      const newComment = await CommentService.createComment(taskId, content);
      setComments(prev => [...prev, newComment]);
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al crear comentario';
      setError(errorMessage);
      console.error('Error creating comment:', err);
      return false;
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  /**
   * Update an existing comment
   */
  const updateComment = useCallback(async (commentId: number, content: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const updatedComment = await CommentService.updateComment(commentId, content);
      setComments(prev => 
        prev.map(comment => comment.id === commentId ? updatedComment : comment)
      );
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al actualizar comentario';
      setError(errorMessage);
      console.error('Error updating comment:', err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Delete a comment
   */
  const deleteComment = useCallback(async (commentId: number): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      await CommentService.deleteComment(commentId);
      setComments(prev => prev.filter(comment => comment.id !== commentId));
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al eliminar comentario';
      setError(errorMessage);
      console.error('Error deleting comment:', err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Auto-fetch comments on mount if enabled
   */
  useEffect(() => {
    if (autoFetch && taskId) {
      fetchComments();
    }
  }, [taskId, autoFetch, fetchComments]);

  return {
    comments,
    loading,
    error,
    fetchComments,
    createComment,
    updateComment,
    deleteComment,
    hasComments: comments.length > 0,
    commentCount: comments.length
  };
};
