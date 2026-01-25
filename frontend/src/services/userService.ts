import api from '../api/axios';
import { User, UserCreate } from '../types';

/**
 * UserService - Service layer for user-related operations
 * 
 * Following SOLID principles:
 * - Single Responsibility: Handles only user-related API calls
 * - Dependency Inversion: Depends on axios abstraction
 * - Open/Closed: Easy to extend with new user operations
 */
export const UserService = {
  /**
   * Get the current authenticated user
   * @returns Current user information
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/users/me');
    return response.data;
  },

  /**
   * Get all users (requires appropriate permissions)
   * @returns Array of all users
   */
  getAllUsers: async (): Promise<User[]> => {
    const response = await api.get<User[]>('/users');
    return response.data;
  },

  /**
   * Create a new user (OWNER role only)
   * @param userData - User data for creation
   * @returns The created user
   */
  createUser: async (userData: UserCreate): Promise<User> => {
    const response = await api.post<User>('/users', userData);
    return response.data;
  }
};
