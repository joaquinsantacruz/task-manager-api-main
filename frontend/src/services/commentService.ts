import api from '../api/axios';
import { Comment, CommentCreate, CommentUpdate } from '../types';

/**
 * CommentService - Service layer for comment-related operations
 * 
 * Following SOLID principles:
 * - Single Responsibility: Handles only comment-related API calls
 * - Dependency Inversion: Depends on axios abstraction, not concrete HTTP implementation
 * - Open/Closed: Easy to extend with new methods without modifying existing ones
 */
export const CommentService = {
  /**
   * Get all comments for a specific task
   * @param taskId - The ID of the task
   * @param params - Optional pagination parameters
   * @returns Array of comments
   */
  getTaskComments: async (
    taskId: number, 
    params?: { skip?: number; limit?: number }
  ): Promise<Comment[]> => {
    const response = await api.get<Comment[]>(`/tasks/${taskId}/comments`, { params });
    return response.data;
  },

  /**
   * Create a new comment on a task
   * @param taskId - The ID of the task
   * @param content - The comment content
   * @returns The created comment
   */
  createComment: async (taskId: number, content: string): Promise<Comment> => {
    const payload: CommentCreate = { content };
    const response = await api.post<Comment>(`/tasks/${taskId}/comments`, payload);
    return response.data;
  },

  /**
   * Update an existing comment
   * @param commentId - The ID of the comment to update
   * @param content - The new comment content
   * @returns The updated comment
   */
  updateComment: async (commentId: number, content: string): Promise<Comment> => {
    const payload: CommentUpdate = { content };
    const response = await api.put<Comment>(`/comments/${commentId}`, payload);
    return response.data;
  },

  /**
   * Delete a comment
   * @param commentId - The ID of the comment to delete
   */
  deleteComment: async (commentId: number): Promise<void> => {
    await api.delete(`/comments/${commentId}`);
  }
};
