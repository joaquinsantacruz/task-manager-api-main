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
    <div className="min-h-screen bg-gray-50 py-8 animate-fade-in animate-slide-up">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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
