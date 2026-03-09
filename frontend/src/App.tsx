import { Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { useNotifications } from './hooks/useNotifications';
import { useNotificationPolling } from './hooks/useNotificationPolling';
import Login from './pages/Login';
import Tasks from './pages/Tasks';
import Notifications from './pages/Notifications';
import { NotificationBell } from './components/notifications';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Cargando...</div>;
  if (!user) return <Navigate to="/login" />;
  
  return children;
};

function AppContent() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const {
    notifications,
    unreadCount,
    markAsRead,
    deleteNotification,
    refresh
  } = useNotifications(!!user);

  // Auto-refresh notifications every 30 seconds when user is logged in
  useNotificationPolling(
    () => {
      if (user) {
        refresh();
      }
    },
    30000,
    !!user
  );

  const handleNotificationClick = () => {
    // Navigate to notifications page is handled by Link in NotificationBell
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      {/* El header se mostrará en todas las páginas */}
      <header className="sticky top-0 z-50 w-full bg-white/80 backdrop-blur-md border-b border-gray-200 text-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-primary-900 tracking-tight">Task Manager</h1>
            
            {user && (
              <div className="flex items-center space-x-6">
                <nav className="flex space-x-2">
                  <Link 
                    to="/tasks"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      location.pathname === '/tasks' 
                        ? 'bg-primary-50 text-primary-700' 
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                  >
                    Tareas
                  </Link>
                  <Link 
                    to="/notifications"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      location.pathname === '/notifications' 
                        ? 'bg-primary-50 text-primary-700' 
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                  >
                    Notificaciones
                  </Link>
                </nav>

                <div className="text-gray-500 hover:text-primary-600 transition-colors">
                  <NotificationBell
                    notifications={notifications}
                    unreadCount={unreadCount}
                    onMarkAsRead={markAsRead}
                    onDelete={deleteNotification}
                    onViewAll={handleNotificationClick}
                  />
                </div>

                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-600 font-medium">
                    {user?.user?.email}
                  </span>
                  <button 
                    onClick={logout} 
                    className="btn-secondary text-sm"
                  >
                    Cerrar Sesión
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          {/* Ruta Pública */}
          <Route path="/login" element={<Login />} />
          
          {/* Rutas Privadas */}
          <Route 
            path="/tasks" 
            element={
              <ProtectedRoute>
                <Tasks />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/notifications" 
            element={
              <ProtectedRoute>
                <Notifications />
              </ProtectedRoute>
            } 
          />
          
          {/* Redirección por defecto: Si entra a raíz, va a tasks (o login si no está auth) */}
          <Route path="*" element={<Navigate to="/tasks" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App