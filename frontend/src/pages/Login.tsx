import { useState, FormEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

/**
 * Login Page Component
 * 
 * Provides user authentication interface with email/password credentials.
 * Handles login form submission, error display, and navigation on success.
 * 
 * Features:
 *   - Email and password input fields
 *   - Form validation and submission
 *   - Error message display
 *   - Automatic navigation to /tasks on successful login
 *   - Integration with AuthContext for authentication
 * 
 * @example
 * ```tsx
 * // In router configuration:
 * <Route path="/login" element={<Login />} />
 * ```
 * 
 * User Flow:
 *   1. User enters email and password
 *   2. Submits form
 *   3. On success: Redirects to /tasks page
 *   4. On error: Displays error message below title
 * 
 * Styling:
 *   - Centered login container
 *   - Error messages in red
 *   - Standard form inputs and submit button
 * 
 * Security:
 *   - Credentials sent via FormData to backend
 *   - Password field uses type="password" (masked input)
 *   - Error messages are generic to prevent enumeration attacks
 */
export default function Login() {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  
  const { login } = useAuth();
  const navigate = useNavigate();

  /**
   * Handle form submission
   * Attempts to authenticate user and navigate to tasks page on success
   */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    const result = await login(email, password);
    
    if (result.success) {
      navigate('/tasks');
    } else {
      // 3. TypeScript nos avisará que 'result.error' es opcional (string | undefined).
      // Debemos proveer un fallback (||) por si viene undefined.
      setError(result.error || 'Ocurrió un error al iniciar sesión');
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 animate-fade-in">
      <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-2xl shadow-xl border border-gray-100">
        <div>
          <h2 className="mt-2 text-center text-3xl font-extrabold text-gray-900 tracking-tight">
            Iniciar Sesión
          </h2>
          <p className="mt-3 text-center text-sm text-gray-500">
            Bienvenido de nuevo a su gestor de tareas
          </p>
        </div>
        
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md animate-fade-in">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700 font-medium">{error}</p>
              </div>
            </div>
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4 shadow-sm">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="email">Email</label>
              <input 
                id="email"
                type="text" 
                placeholder="ejemplo@correo.com" 
                className="input-field"
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="password">Contraseña</label>
              <input 
                id="password"
                type="password" 
                placeholder="••••••••" 
                className="input-field"
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                required
              />
            </div>
          </div>

          <div>
            <button 
              type="submit" 
              className="w-full btn-primary py-3 text-base flex justify-center items-center group relative overflow-hidden"
            >
              <span className="absolute w-0 h-0 transition-all duration-300 ease-out bg-white rounded-full group-hover:w-full group-hover:h-32 opacity-10"></span>
              <span className="relative">Entrar al Sistema</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}