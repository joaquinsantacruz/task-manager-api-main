import api from '../api/axios';
import { Task, CreateTaskDTO, UpdateTaskDTO, TaskStatus } from '../types';

/**
 * TaskService - Service layer for task-related operations
 * 
 * Following SOLID principles:
 * - Single Responsibility: Handles only task-related API calls
 * - Dependency Inversion: Depends on axios abstraction
 * - Open/Closed: Easy to extend with new task operations
 */
export const TaskService = {
  /**
   * Get all tasks with optional filtering
   * @param params - Optional parameters for filtering and pagination
   * @returns Array of tasks
   */
  getAll: async (params?: { skip?: number; limit?: number; only_mine?: boolean }): Promise<Task[]> => {
    const response = await api.get<Task[]>('/tasks', { params });
    return response.data;
  },

  /**
   * Get a specific task by ID
   * @param id - The task ID
   * @returns The task
   */
  getById: async (id: number): Promise<Task> => {
    const response = await api.get<Task>(`/tasks/${id}`);
    return response.data;
  },

  /**
   * Create a new task
   * @param taskData - Data for creating the task
   * @returns The created task
   */
  create: async (taskData: CreateTaskDTO): Promise<Task> => {
    const response = await api.post<Task>('/tasks', taskData);
    return response.data;
  },

  /**
   * Update a task
   * @param id - The task ID
   * @param updates - Fields to update
   * @returns The updated task
   */
  update: async (id: number, updates: UpdateTaskDTO): Promise<Task> => {
    const response = await api.put<Task>(`/tasks/${id}`, updates);
    return response.data;
  },

  /**
   * Update only the status of a task
   * @param id - The task ID
   * @param newStatus - The new status
   * @returns The updated task
   */
  updateStatus: async (id: number, newStatus: TaskStatus): Promise<Task> => {
    const payload: UpdateTaskDTO = { status: newStatus };
    const response = await api.put<Task>(`/tasks/${id}`, payload);
    return response.data;
  },

  /**
   * Delete a task
   * @param id - The task ID
   */
  delete: async (id: number): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },

  /**
   * Change the owner of a task (OWNER role only)
   * @param id - The task ID
   * @param newOwnerId - The ID of the new owner
   * @returns The updated task
   */
  changeOwner: async (id: number, newOwnerId: number): Promise<Task> => {
    const response = await api.patch<Task>(`/tasks/${id}/owner`, { owner_id: newOwnerId });
    return response.data;
  }
};