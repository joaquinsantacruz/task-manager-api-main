import { Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { useNotifications } from './hooks/useNotifications';
import { useNotificationPolling } from './hooks/useNotificationPolling';
import Login from './pages/Login';
import Tasks from './pages/Tasks';
import Notifications from './pages/Notifications';
import { NotificationBell } from './components/notifications';
import './App.css';

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
    <div className="App">
      {/* El header se mostrará en todas las páginas */}
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        padding: '1rem 2rem',
        backgroundColor: '#282c34',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <h1 style={{ margin: 0 }}>Task Manager</h1>
        
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
            <nav style={{ display: 'flex', gap: '1.5rem' }}>
              <Link 
                to="/tasks"
                style={{
                  textDecoration: 'none',
                  color: location.pathname === '/tasks' ? '#007bff' : 'white',
                  fontWeight: location.pathname === '/tasks' ? 'bold' : 'normal',
                  padding: '0.5rem 1rem'
                }}
              >
                Tareas
              </Link>
              <Link 
                to="/notifications"
                style={{
                  textDecoration: 'none',
                  color: location.pathname === '/notifications' ? '#007bff' : 'white',
                  fontWeight: location.pathname === '/notifications' ? 'bold' : 'normal',
                  padding: '0.5rem 1rem'
                }}
              >
                Notificaciones
              </Link>
            </nav>

            <NotificationBell
              notifications={notifications}
              unreadCount={unreadCount}
              onMarkAsRead={markAsRead}
              onDelete={deleteNotification}
              onViewAll={handleNotificationClick}
            />

            <button 
              onClick={logout} 
              style={{ 
                background: '#333', 
                color: 'white', 
                padding: '0.5rem 1rem', 
                border: 'none', 
                borderRadius: '4px', 
                cursor: 'pointer' 
              }}
            >
              Cerrar Sesión
            </button>
          </div>
        )}
      </header>

      <main>
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