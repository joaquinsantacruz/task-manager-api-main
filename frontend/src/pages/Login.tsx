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
    <div className="login-container">
      <h2>Iniciar Sesión</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          placeholder="Email / Username" 
          value={email} 
          onChange={(e) => setEmail(e.target.value)} 
        />
        <input 
          type="password" 
          placeholder="Password" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
        />
        <button type="submit">Entrar</button>
      </form>
    </div>
  );
}