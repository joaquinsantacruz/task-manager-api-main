import { useState } from 'react';
import { Notification } from '../../types';
import { NotificationItem } from './';

/**
 * NotificationList - Component for displaying full notification list with filters
 * 
 */
interface NotificationListProps {
  notifications: Notification[];
  loading: boolean;
  onMarkAsRead: (id: number) => void;
  onDelete: (id: number) => void;
  onMarkAllAsRead?: () => void;
  onNotificationClick?: (taskId: number) => void;
}

export default function NotificationList({
  notifications,
  loading,
  onMarkAsRead,
  onDelete,
  onMarkAllAsRead,
  onNotificationClick
}: NotificationListProps) {
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  const filteredNotifications = filter === 'unread'
    ? notifications.filter(n => !n.is_read)
    : notifications;

  const unreadCount = notifications.filter(n => !n.is_read).length;

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: '#666' }}>
        Cargando notificaciones...
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '1rem' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1.5rem'
      }}>
        <h2 style={{ margin: 0 }}>Notificaciones</h2>
        
        {unreadCount > 0 && onMarkAllAsRead && (
          <button
            onClick={onMarkAllAsRead}
            style={{
              padding: '0.5rem 1rem',
              border: '1px solid #007bff',
              borderRadius: '4px',
              background: 'white',
              color: '#007bff',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            Marcar todas como leídas
          </button>
        )}
      </div>

      <div style={{
        display: 'flex',
        gap: '1rem',
        marginBottom: '1.5rem',
        borderBottom: '2px solid #eee'
      }}>
        <button
          onClick={() => setFilter('all')}
          style={{
            padding: '0.75rem 1.5rem',
            border: 'none',
            background: 'transparent',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: filter === 'all' ? 'bold' : 'normal',
            color: filter === 'all' ? '#007bff' : '#666',
            borderBottom: filter === 'all' ? '2px solid #007bff' : 'none',
            marginBottom: '-2px'
          }}
        >
          Todas ({notifications.length})
        </button>
        <button
          onClick={() => setFilter('unread')}
          style={{
            padding: '0.75rem 1.5rem',
            border: 'none',
            background: 'transparent',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: filter === 'unread' ? 'bold' : 'normal',
            color: filter === 'unread' ? '#007bff' : '#666',
            borderBottom: filter === 'unread' ? '2px solid #007bff' : 'none',
            marginBottom: '-2px'
          }}
        >
          No leídas ({unreadCount})
        </button>
      </div>

      {filteredNotifications.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '3rem',
          color: '#999',
          fontStyle: 'italic',
          backgroundColor: '#f9f9f9',
          borderRadius: '8px',
          border: '1px dashed #ddd'
        }}>
          {filter === 'unread' 
            ? 'No tienes notificaciones sin leer' 
            : 'No tienes notificaciones'}
        </div>
      ) : (
        <div>
          {filteredNotifications.map(notification => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              onMarkAsRead={onMarkAsRead}
              onDelete={onDelete}
              onClick={onNotificationClick}
            />
          ))}
        </div>
      )}
    </div>
  );
}
