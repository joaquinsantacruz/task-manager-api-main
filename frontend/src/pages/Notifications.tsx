import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { NotificationList } from '../components/notifications';
import { useNotifications } from '../hooks/useNotifications';

/**
 * Notifications Page - Full page view for managing notifications
 * 
 * Following SOLID principles:
 * - Single Responsibility: Displays and manages notifications
 * - Dependency Inversion: Uses useNotifications hook abstraction
 */
export default function Notifications() {
  const navigate = useNavigate();
  const {
    notifications,
    loading,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    refresh
  } = useNotifications(true);

  useEffect(() => {
    // Refresh notifications when component mounts
    refresh();
  }, []);

  const handleNotificationClick = (_taskId: number) => {
    // Navigate to tasks page (could be enhanced to open specific task)
    navigate('/tasks');
  };

  return (
    <div style={{ 
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      paddingTop: '2rem',
      paddingBottom: '2rem'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem' }}>
        <NotificationList
          notifications={notifications}
          loading={loading}
          onMarkAsRead={markAsRead}
          onDelete={deleteNotification}
          onMarkAllAsRead={markAllAsRead}
          onNotificationClick={handleNotificationClick}
        />
      </div>
    </div>
  );
}
