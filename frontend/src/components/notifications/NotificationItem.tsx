import { Notification, NotificationType } from '../../types';

/**
 * NotificationItem - Component for displaying a single notification
 * 
 */
interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: number) => void;
  onDelete: (id: number) => void;
  onClick?: (taskId: number) => void;
}

export default function NotificationItem({ notification, onMarkAsRead, onDelete, onClick }: NotificationItemProps) {
  const getNotificationColor = (type: NotificationType): string => {
    switch (type) {
      case 'overdue':
        return '#dc3545';
      case 'due_today':
        return '#ffc107';
      case 'due_soon':
        return '#17a2b8';
      default:
        return '#6c757d';
    }
  };

  const getNotificationIcon = (type: NotificationType): string => {
    switch (type) {
      case 'overdue':
        return '⚠️';
      case 'due_today':
        return '📅';
      case 'due_soon':
        return '⏰';
      default:
        return '🔔';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Ahora';
    if (diffMins < 60) return `Hace ${diffMins} min`;
    if (diffHours < 24) return `Hace ${diffHours}h`;
    if (diffDays < 7) return `Hace ${diffDays}d`;
    
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const handleClick = () => {
    if (!notification.is_read) {
      onMarkAsRead(notification.id);
    }
    if (onClick) {
      onClick(notification.task_id);
    }
  };

  return (
    <div
      onClick={handleClick}
      style={{
        padding: '0.75rem',
        borderLeft: `4px solid ${getNotificationColor(notification.notification_type)}`,
        backgroundColor: notification.is_read ? '#f9f9f9' : '#fff',
        marginBottom: '0.5rem',
        borderRadius: '4px',
        cursor: onClick ? 'pointer' : 'default',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        boxShadow: notification.is_read ? 'none' : '0 1px 3px rgba(0,0,0,0.1)',
        transition: 'all 0.2s ease'
      }}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.backgroundColor = '#f0f0f0';
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = notification.is_read ? '#f9f9f9' : '#fff';
      }}
    >
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <span style={{ fontSize: '1.2rem' }}>
            {getNotificationIcon(notification.notification_type)}
          </span>
          {!notification.is_read && (
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: '#007bff',
              display: 'inline-block'
            }} />
          )}
          <span style={{ fontSize: '0.85rem', color: '#666' }}>
            {formatDate(notification.created_at)}
          </span>
        </div>
        
        <p style={{ 
          margin: '0.5rem 0 0.25rem 0', 
          color: '#333',
          fontWeight: notification.is_read ? 'normal' : 'bold'
        }}>
          {notification.message}
        </p>
        
        {notification.task_title && (
          <p style={{ 
            margin: 0, 
            fontSize: '0.85rem',
            color: '#666',
            fontStyle: 'italic'
          }}>
            Tarea: {notification.task_title}
          </p>
        )}
      </div>

      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete(notification.id);
        }}
        style={{
          padding: '0.25rem 0.5rem',
          border: 'none',
          background: 'transparent',
          color: '#999',
          cursor: 'pointer',
          fontSize: '1.2rem',
          marginLeft: '0.5rem'
        }}
        title="Eliminar notificación"
      >
        ×
      </button>
    </div>
  );
}
