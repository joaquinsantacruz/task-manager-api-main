import { useState, useRef, useEffect } from 'react';
import { Notification } from '../../types';
import { NotificationItem } from './';

/**
 * NotificationBell - Component for notification bell icon with dropdown
 * 
 */
interface NotificationBellProps {
  notifications: Notification[];
  unreadCount: number;
  onMarkAsRead: (id: number) => void;
  onDelete: (id: number) => void;
  onViewAll?: () => void;
  onNotificationClick?: (taskId: number) => void;
}

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
