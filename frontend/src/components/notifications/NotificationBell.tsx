import { useState, useRef, useEffect } from 'react';
import { Notification } from '../../types';
import { NotificationItem } from './';

/**
 * NotificationBell Component Props
 */
interface NotificationBellProps {
  /** Array of all user notifications */
  notifications: Notification[];
  
  /** Total count of unread notifications */
  unreadCount: number;
  
  /** Callback when notification is marked as read */
  onMarkAsRead: (id: number) => void;
  
  /** Callback when notification is deleted */
  onDelete: (id: number) => void;
  
  /** Optional callback when "View All" is clicked */
  onViewAll?: () => void;
  
  /** Optional callback when notification is clicked (receives task ID) */
  onNotificationClick?: (taskId: number) => void;
}

/**
 * NotificationBell Component
 * 
 * Displays a bell icon with unread count badge and dropdown list of recent notifications.
 * Provides quick access to notifications without navigating away from current page.
 * 
 * Features:
 *   - Shows unread notification count badge (displays "9+" for 10 or more)
 *   - Dropdown with 5 most recent notifications
 *   - Click outside to close dropdown
 *   - Supports marking as read and deleting notifications
 *   - Optional "View All" button to navigate to full notifications page
 *   - Optional click handler for notification-to-task navigation
 * 
 * @param notifications - Array of all user notifications
 * @param unreadCount - Total count of unread notifications
 * @param onMarkAsRead - Function called when marking notification as read
 * @param onDelete - Function called when deleting notification
 * @param onViewAll - Optional function called when clicking "View All"
 * @param onNotificationClick - Optional function called when clicking notification
 * 
 * @example
 * ```tsx
 * <NotificationBell
 *   notifications={notifications}
 *   unreadCount={unreadCount}
 *   onMarkAsRead={handleMarkAsRead}
 *   onDelete={handleDelete}
 *   onViewAll={() => navigate('/notifications')}
 *   onNotificationClick={(taskId) => navigate(`/tasks/${taskId}`)}
 * />
 * ```
 * 
 * Behavior:
 *   - Only shows 5 most recent notifications in dropdown
 *   - Badge shows "9+" for 10 or more unread notifications
 *   - Clicking outside dropdown closes it
 *   - Bell icon toggles dropdown open/closed
 * 
 * Styling:
 *   - Bell emoji: 🔔
 *   - Red badge for unread count
 *   - White dropdown with shadow
 *   - Absolute positioning for dropdown
 */

export default function NotificationBell({
  notifications,
  unreadCount,
  onMarkAsRead,
  onDelete,
  onViewAll,
  onNotificationClick
}: NotificationBellProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const recentNotifications = notifications.slice(0, 5);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative bg-transparent border-none cursor-pointer p-2 text-2xl text-gray-700 hover:text-primary-600 transition-colors"
        title="Notificaciones"
      >
        <span role="img" aria-label="Notificaciones">🔔</span>
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-[0.7rem] font-bold shadow-sm border-2 border-white">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-96 max-h-[500px] bg-white border border-gray-100 rounded-xl shadow-xl z-50 overflow-hidden flex flex-col animate-fade-in">
          <div className="p-4 border-b border-gray-100 font-bold text-lg flex justify-between items-center bg-gray-50/80 backdrop-blur-sm">
            <span className="text-gray-900 tracking-tight">Notificaciones</span>
            {unreadCount > 0 && (
              <span className="text-sm text-primary-600 font-medium bg-primary-50 px-2 py-0.5 rounded-full">
                {unreadCount} sin leer
              </span>
            )}
          </div>

          <div className="flex-1 overflow-y-auto p-2">
            {recentNotifications.length === 0 ? (
              <div className="text-center p-8 text-gray-400 italic">
                No tienes notificaciones
              </div>
            ) : (
              recentNotifications.map(notification => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onMarkAsRead={onMarkAsRead}
                  onDelete={onDelete}
                  onClick={onNotificationClick}
                />
              ))
            )}
          </div>

          {notifications.length > 5 && onViewAll && (
            <div className="border-t border-gray-100 p-3 text-center bg-gray-50/50">
              <button
                onClick={() => {
                  setIsOpen(false);
                  onViewAll();
                }}
                className="bg-transparent border-none text-primary-600 hover:text-primary-700 cursor-pointer text-sm font-bold transition-colors"
              >
                Ver todas las notificaciones
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
