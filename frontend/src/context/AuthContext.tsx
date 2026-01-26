import { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import api from '../api/axios';
import { AuthSession, User } from '../types';
import { UserService } from '../services/userService';

/**
 * Authentication Context Interface
 * 
 * Defines the shape of the authentication context available to consuming components.
 */
interface AuthContextType {
  /** Current authenticated user session (null if not logged in) */
  user: AuthSession | null;
  
  /** 
   * Authenticate user with credentials
   * @param username - User's email address
   * @param password - User's password
   * @returns Object with success status and optional error message
   */
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  
  /** Log out the current user and clear session */
  logout: () => void;
  
  /** Loading state during initial authentication check */
  loading: boolean;
}

/**
 * Authentication Context
 * 
 * Provides authentication state and methods throughout the application.
 * Must be consumed via useAuth() hook.
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider Component
 * 
 * Wraps the application to provide authentication context to all child components.
 * Handles token persistence, automatic login restoration, and session management.
 * 
 * Features:
 *   - Automatic token restoration from localStorage on mount
 *   - Fetches user data after token restoration
 *   - Persists token across browser sessions
 *   - Provides centralized login/logout functionality
 * 
 * @param children - Child components that will have access to auth context
 * 
 * @example
 * ```tsx
 * <AuthProvider>
 *   <App />
 * </AuthProvider>
 * ```
 */
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  // 4. Usamos Genéricos <AuthSession | null> para que TS acepte objetos o nulos
  const [user, setUser] = useState<AuthSession | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Obtener información del usuario
      UserService.getCurrentUser()
        .then(userData => {
          setUser({ token, user: userData });
        })
        .catch(() => {
          // Si falla, solo guardar el token
          setUser({ token });
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  // 5. Tipamos los argumentos
  const login = async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      // Tipamos la respuesta esperada de Axios (si quieres ser estricto)
      const response = await api.post<{ access_token: string }>('/login/access-token', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      
      // Obtener información del usuario después del login
      try {
        const userData = await UserService.getCurrentUser();
        setUser({ token: access_token, user: userData });
      } catch {
        setUser({ token: access_token });
      }
      
      return { success: true };
    } catch (error: any) { // 6. Manejo de error (any o unknown)
      const errorMessage = error.response?.data?.detail || 'Login failed';
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

/**
 * useAuth Hook
 * 
 * Custom hook to access authentication context from any component.
 * Must be used within an AuthProvider.
 * 
 * @returns AuthContextType object containing:
 *   - user: Current authenticated user session
 *   - login: Function to authenticate user
 *   - logout: Function to log out user
 *   - loading: Boolean indicating if initial auth check is in progress
 * 
 * @throws Error if used outside of AuthProvider
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { user, login, logout } = useAuth();
 *   
 *   if (!user) {
 *     return <div>Please log in</div>;
 *   }
 *   
 *   return <div>Welcome {user.user?.email}</div>;
 * }
 * ```
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe ser usado dentro de un AuthProvider");
  }
  return context;
};