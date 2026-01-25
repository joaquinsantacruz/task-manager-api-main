import { useState, useCallback, useEffect } from 'react';
import { NotificationService } from '../services/notificationService';
import { Notification } from '../types';

/**
 * useNotifications - Custom hook for managing user notifications
 * 
 * Following SOLID principles:
 * - Single Responsibility: Manages notification state and operations
 * - Dependency Inversion: Depends on NotificationService abstraction
 * - Open/Closed: Easy to extend with new notification features
 * 
 * @param autoFetch - Whether to automatically fetch notifications on mount
 * @returns Notification state and operations
 */
export const useNotifications = (autoFetch: boolean = true) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch notifications with optional filters
   */
  const fetchNotifications = useCallback(async (unreadOnly: boolean = false) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await NotificationService.getNotifications({ 
        unread_only: unreadOnly 
      });
      setNotifications(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar notificaciones';
      setError(errorMessage);
      console.error('Error fetching notifications:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Fetch unread notification count
   */
  const fetchUnreadCount = useCallback(async () => {
    try {
      const response = await NotificationService.getUnreadCount();
      setUnreadCount(response.unread_count);
    } catch (err) {
      console.error('Error fetching unread count:', err);
    }
  }, []);

  /**
   * Mark a notification as read
   */
  const markAsRead = useCallback(async (notificationId: number): Promise<boolean> => {
    try {
      const updatedNotification = await NotificationService.markAsRead(notificationId);
      
      // Update local state
      setNotifications(prev => 
        prev.map(notif => notif.id === notificationId ? updatedNotification : notif)
      );
      
      // Decrease unread count if notification was unread
      const wasUnread = notifications.find(n => n.id === notificationId)?.is_read === false;
      if (wasUnread) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      
      return true;
    } catch (err) {
      console.error('Error marking notification as read:', err);
      return false;
    }
  }, [notifications]);

  /**
   * Mark all notifications as read
   */
  const markAllAsRead = useCallback(async (): Promise<boolean> => {
    try {
      const unreadNotifications = notifications.filter(n => !n.is_read);
      
      await Promise.all(
        unreadNotifications.map(notif => NotificationService.markAsRead(notif.id))
      );
      
      // Update local state
      setNotifications(prev => 
        prev.map(notif => ({ ...notif, is_read: true }))
      );
      
      setUnreadCount(0);
      return true;
    } catch (err) {
      console.error('Error marking all notifications as read:', err);
      return false;
    }
  }, [notifications]);

  /**
   * Delete a notification
   */
  const deleteNotification = useCallback(async (notificationId: number): Promise<boolean> => {
    try {
      await NotificationService.deleteNotification(notificationId);
      
      // Update local state
      const wasUnread = notifications.find(n => n.id === notificationId)?.is_read === false;
      setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
      
      if (wasUnread) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      
      return true;
    } catch (err) {
      console.error('Error deleting notification:', err);
      return false;
    }
  }, [notifications]);

  /**
   * Refresh both notifications and unread count
   */
  const refresh = useCallback(async () => {
    await Promise.all([
      fetchNotifications(),
      fetchUnreadCount()
    ]);
  }, [fetchNotifications, fetchUnreadCount]);

  /**
   * Auto-fetch on mount if enabled
   */
  useEffect(() => {
    if (autoFetch) {
      refresh();
    }
  }, [autoFetch]); // Intentionally omit refresh to avoid infinite loop

  return {
    notifications,
    unreadCount,
    loading,
    error,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    refresh,
    hasNotifications: notifications.length > 0,
    hasUnread: unreadCount > 0
  };
};
