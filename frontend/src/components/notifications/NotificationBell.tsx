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
    <div style={{ position: 'relative' }} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'relative',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          padding: '0.5rem',
          fontSize: '1.5rem',
          color: '#333'
        }}
        title="Notificaciones"
      >
        🔔
        {unreadCount > 0 && (
          <span style={{
            position: 'absolute',
            top: '0',
            right: '0',
            background: '#dc3545',
            color: 'white',
            borderRadius: '50%',
            width: '20px',
            height: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.7rem',
            fontWeight: 'bold'
          }}>
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute',
          top: '100%',
          right: '0',
          marginTop: '0.5rem',
          width: '400px',
          maxHeight: '500px',
          backgroundColor: 'white',
          border: '1px solid #ddd',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          zIndex: 1000,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{
            padding: '1rem',
            borderBottom: '1px solid #eee',
            fontWeight: 'bold',
            fontSize: '1.1rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span>Notificaciones</span>
            {unreadCount > 0 && (
              <span style={{
                fontSize: '0.85rem',
                color: '#007bff',
                fontWeight: 'normal'
              }}>
                {unreadCount} sin leer
              </span>
            )}
          </div>

          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '0.5rem'
          }}>
            {recentNotifications.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '2rem',
                color: '#999',
                fontStyle: 'italic'
              }}>
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
            <div style={{
              borderTop: '1px solid #eee',
              padding: '0.75rem',
              textAlign: 'center'
            }}>
              <button
                onClick={() => {
                  setIsOpen(false);
                  onViewAll();
                }}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#007bff',
                  cursor: 'pointer',
                  fontSize: '0.95rem',
                  fontWeight: 'bold'
                }}
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
