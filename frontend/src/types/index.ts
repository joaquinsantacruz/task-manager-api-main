export type UserRole = 'owner' | 'member';
export type TaskStatus = 'todo' | 'in_progress' | 'done';

export interface AuthSession {
  token: string;
  user?: User;
}

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  role: UserRole;
  created_at: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string | null;
  status: TaskStatus;
  owner_id: number;
  owner_email?: string;
  created_at: string;
  updated_at?: string | null;
}

export interface CreateTaskDTO {
  title: string;
  description?: string; 
  status?: TaskStatus;
}

export interface UpdateTaskDTO {
  title?: string;
  description?: string;
  status?: TaskStatus;
}