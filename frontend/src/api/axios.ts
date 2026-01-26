import axios, { InternalAxiosRequestConfig } from 'axios';

/**
 * Axios API Client Configuration
 * 
 * Pre-configured axios instance for making HTTP requests to the backend API.
 * Includes automatic token injection and authentication error handling.
 * 
 * Base Configuration:
 *   - baseURL: http://localhost:8000/api/v1
 *   - Content-Type: application/json
 * 
 * Request Interceptor:
 *   - Automatically adds JWT token from localStorage to Authorization header
 *   - Token format: "Bearer {token}"
 *   - Applied to all outgoing requests
 * 
 * Response Interceptor:
 *   - Handles 401 (Unauthorized) and 403 (Forbidden) errors
 *   - Automatically logs out user and redirects to /login
 *   - Clears token from localStorage on authentication failure
 * 
 * Usage:
 *   ```typescript
 *   import api from './api/axios';
 *   const response = await api.get('/tasks');
 *   ```
 * 
 * Security:
 *   - Token is stored in localStorage (consider httpOnly cookies for production)
 *   - Automatic redirect prevents unauthorized access
 *   - All requests include authentication token when available
 */
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;