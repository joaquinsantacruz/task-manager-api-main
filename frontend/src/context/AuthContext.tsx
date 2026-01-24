import { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import api from '../api/axios';
import { AuthSession, User } from '../types';
import { UserService } from '../services/userService';

// 2. Definimos la forma del Contexto
interface AuthContextType {
  user: AuthSession | null;
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 3. Corregimos la sintaxis de las props ({ children })
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

// 7. Hook personalizado protegido
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe ser usado dentro de un AuthProvider");
  }
  return context;
};