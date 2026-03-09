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
      <div className="text-center py-12 text-gray-500 animate-pulse font-medium">
        Cargando notificaciones...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-4 bg-white/50 backdrop-blur-sm rounded-2xl shadow-sm border border-gray-100">
      <div className="flex justify-between items-center mb-8 bg-white p-6 rounded-xl shadow-sm">
        <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight m-0">Notificaciones</h2>
        
        {unreadCount > 0 && onMarkAllAsRead && (
          <button
            onClick={onMarkAllAsRead}
            className="btn-secondary flex items-center gap-2 hover:bg-gray-50 border-gray-300"
          >
            <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
            Marcar todas como leídas
          </button>
        )}
      </div>

      <div className="flex gap-2 mb-8 border-b-2 border-gray-100">
        <button
          onClick={() => setFilter('all')}
          className={`px-6 py-3 font-medium text-sm transition-all -mb-0.5 border-b-2 ${
            filter === 'all' 
              ? 'text-primary-600 border-primary-600 bg-primary-50/50 rounded-t-lg' 
              : 'text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-50 rounded-t-lg'
          }`}
        >
          Todas <span className={`ml-1 px-2 py-0.5 rounded-full text-xs ${filter === 'all' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'}`}>{notifications.length}</span>
        </button>
        <button
          onClick={() => setFilter('unread')}
          className={`px-6 py-3 font-medium text-sm transition-all -mb-0.5 border-b-2 ${
            filter === 'unread' 
              ? 'text-primary-600 border-primary-600 bg-primary-50/50 rounded-t-lg' 
              : 'text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-50 rounded-t-lg'
          }`}
        >
          No leídas <span className={`ml-1 px-2 py-0.5 rounded-full text-xs ${filter === 'unread' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'}`}>{unreadCount}</span>
        </button>
      </div>

      {filteredNotifications.length === 0 ? (
        <div className="text-center py-16 px-4 bg-gray-50/50 rounded-xl border-2 border-dashed border-gray-200">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <p className="text-gray-500 font-medium">
            {filter === 'unread' 
              ? 'No tienes notificaciones sin leer' 
              : 'No tienes notificaciones'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
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
