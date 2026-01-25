import api from '../api/axios';
import { Notification, UnreadCountResponse, NotificationGenerationResponse } from '../types';

/**
 * NotificationService - Service layer for notification-related operations
 * 
 * Following SOLID principles:
 * - Single Responsibility: Handles only notification-related API calls
 * - Dependency Inversion: Depends on axios abstraction
 * - Open/Closed: Easy to extend with new notification types
 */
export const NotificationService = {
  /**
   * Get all notifications for the current user
   * @param params - Optional filtering and pagination parameters
   * @returns Array of notifications
   */
  getNotifications: async (params?: {
    unread_only?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<Notification[]> => {
    const response = await api.get<Notification[]>('/notifications', { params });
    return response.data;
  },

  /**
   * Get the count of unread notifications
   * @returns Object containing unread_count
   */
  getUnreadCount: async (): Promise<UnreadCountResponse> => {
    const response = await api.get<UnreadCountResponse>('/notifications/unread-count');
    return response.data;
  },

  /**
   * Mark a notification as read
   * @param notificationId - The ID of the notification to mark as read
   * @returns The updated notification
   */
  markAsRead: async (notificationId: number): Promise<Notification> => {
    const response = await api.put<Notification>(`/notifications/${notificationId}/read`);
    return response.data;
  },

  /**
   * Delete a notification
   * @param notificationId - The ID of the notification to delete
   */
  deleteNotification: async (notificationId: number): Promise<void> => {
    await api.delete(`/notifications/${notificationId}`);
  },

  /**
   * Trigger generation of due date notifications (OWNER role only)
   * This should typically run automatically via scheduler in production
   * @returns Response with count of notifications created
   */
  checkDueDates: async (): Promise<NotificationGenerationResponse> => {
    const response = await api.post<NotificationGenerationResponse>('/notifications/check-due-dates');
    return response.data;
  }
};
