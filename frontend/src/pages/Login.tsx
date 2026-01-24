import { useState, FormEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  // TypeScript infiere que son strings por el valor inicial '', 
  // pero puedes ser explícito si prefieres: useState<string>('')
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  
  const { login } = useAuth();
  const navigate = useNavigate();

  // 2. Tipamos el evento 'e' como FormEvent
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(''); // Limpiamos errores previos

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