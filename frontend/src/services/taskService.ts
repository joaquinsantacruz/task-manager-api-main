import api from '../api/axios';
import { Task, CreateTaskDTO, UpdateTaskDTO, TaskStatus } from '../types';

export const TaskService = {
  getAll: async (params?: { skip?: number; limit?: number; only_mine?: boolean }): Promise<Task[]> => {
    const response = await api.get<Task[]>('/tasks', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Task> => {
    const response = await api.get<Task>(`/tasks/${id}`);
    return response.data;
  },

  create: async (title: string, description?: string, status?: TaskStatus): Promise<Task> => {
    const payload: CreateTaskDTO = {
      title,
      description,
      status
    };
    const response = await api.post<Task>('/tasks', payload);
    return response.data;
  },

  update: async (id: number, updates: UpdateTaskDTO): Promise<Task> => {
    const response = await api.put<Task>(`/tasks/${id}`, updates);
    return response.data;
  },

  updateStatus: async (id: number, newStatus: TaskStatus): Promise<Task> => {
    const payload: UpdateTaskDTO = { status: newStatus };
    const response = await api.put<Task>(`/tasks/${id}`, payload);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },

  changeOwner: async (id: number, newOwnerId: number): Promise<Task> => {
    const response = await api.patch<Task>(`/tasks/${id}/owner`, { owner_id: newOwnerId });
    return response.data;
  }
};