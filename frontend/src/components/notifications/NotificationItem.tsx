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
  const getNotificationColorClass = (type: NotificationType): string => {
    switch (type) {
      case 'overdue': return 'border-red-500';
      case 'due_today': return 'border-yellow-400';
      case 'due_soon': return 'border-cyan-500';
      default: return 'border-gray-400';
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
      className={`p-4 mb-3 rounded-lg border-l-4 ${getNotificationColorClass(notification.notification_type)} flex justify-between items-start transition-all duration-200 ease-in-out ${
        onClick ? 'cursor-pointer' : 'cursor-default'
      } ${
        notification.is_read 
          ? 'bg-gray-50 border-gray-200 opacity-75' 
          : 'bg-white shadow-sm hover:shadow-md hover:bg-gray-50'
      }`}
    >
      <div className="flex-1 min-w-0 pr-3">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xl" role="img" aria-label="icono de notificación">
            {getNotificationIcon(notification.notification_type)}
          </span>
          {!notification.is_read && (
            <span className="w-2 h-2 rounded-full bg-primary-500 inline-block shadow-sm"></span>
          )}
          <span className="text-xs text-gray-500 font-medium">
            {formatDate(notification.created_at)}
          </span>
        </div>
        
        <p className={`mt-1.5 mb-1 text-sm ${notification.is_read ? 'text-gray-600 font-normal' : 'text-gray-900 font-bold tracking-tight'}`}>
          {notification.message}
        </p>
        
        {notification.task_title && (
          <p className="m-0 text-xs text-gray-500 italic truncate" title={notification.task_title}>
            Tarea: <span className="font-medium">{notification.task_title}</span>
          </p>
        )}
      </div>

      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete(notification.id);
        }}
        className="p-1 -mr-2 bg-transparent border-none text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg cursor-pointer text-xl flex-shrink-0 transition-colors"
        title="Eliminar notificación"
      >
        &times;
      </button>
    </div>
  );
}
