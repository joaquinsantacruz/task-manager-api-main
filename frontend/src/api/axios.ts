import axios, { InternalAxiosRequestConfig } from 'axios';
import logger from '../utils/logger';

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
 *   - Logs all outgoing requests for debugging
 * 
 * Response Interceptor:
 *   - Handles 401 (Unauthorized) and 403 (Forbidden) errors
 *   - Automatically logs out user and redirects to /login
 *   - Clears token from localStorage on authentication failure
 *   - Logs all responses and errors
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
 * 
 * Environment Variables:
 *   - VITE_API_BASE_URL: Base URL for the API (defaults to http://localhost:8000/api/v1)
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Log outgoing request
  logger.logRequest(config.method || 'GET', config.url || '', config.data);
  
  return config;
});

api.interceptors.response.use(
  (response) => {
    // Log successful response
    logger.logResponse(
      response.config.method || 'GET',
      response.config.url || '',
      response.status
    );
    return response;
  },
  (error) => {
    // Log error response
    if (error.response) {
      logger.error(
        `API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} - Status: ${error.response.status}`,
        error.response.data
      );
    } else {
      logger.error(`Network Error: ${error.message}`, error);
    }
    
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      logger.warn(`Authentication error, redirecting to login`);
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;