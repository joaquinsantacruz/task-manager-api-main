import { useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Tasks from './pages/Tasks';
import './App.css';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Cargando...</div>;
  if (!user) return <Navigate to="/login" />;
  
  return children;
};

function AppContent() {
  const { user, logout } = useAuth();

  return (
    <div className="App">
      {/* El header se mostrará en todas las páginas */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 2rem' }}>
        <h1>Task Manager</h1>
        {user && (
          <button onClick={logout} style={{ background: '#333', color: 'white', padding: '0.5rem 1rem', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Cerrar Sesión
          </button>
        )}
      </header>

      <main>
        <Routes>
          {/* Ruta Pública */}
          <Route path="/login" element={<Login />} />
          
          {/* Ruta Privada */}
          <Route 
            path="/tasks" 
            element={
              <ProtectedRoute>
                <Tasks />
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

  // TODO: Implement your React application
  // Consider:
  // - Login/Register page
  // - Task list view
  // - Task creation form
  // - API integration
  // - State management
  // - Error handling
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App