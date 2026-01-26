// ==================== USER TYPES ====================
export type UserRole = 'owner' | 'member';

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

export interface UserCreate {
  email: string;
  password: string;
  role: UserRole;
}

// ==================== TASK TYPES ====================
export type TaskStatus = 'todo' | 'in_progress' | 'done';

export interface Task {
  id: number;
  title: string;
  description?: string | null;
  status: TaskStatus;
  owner_id: number;
  owner_email?: string;
  created_at: string;
  updated_at?: string | null;
  due_date?: string | null;
}

export interface CreateTaskDTO {
  title: string;
  description?: string; 
  status?: TaskStatus;
  due_date?: string;
}

export interface UpdateTaskDTO {
  title?: string;
  description?: string;
  status?: TaskStatus;
  due_date?: string;
}

// ==================== COMMENT TYPES ====================
export interface Comment {
  id: number;
  content: string;
  task_id: number;
  author_id: number;
  author_email?: string;
  created_at: string;
  updated_at?: string | null;
}

export interface CommentCreate {
  content: string;
}

export interface CommentUpdate {
  content: string;
}

// ==================== NOTIFICATION TYPES ====================
export type NotificationType = 'due_today' | 'due_soon' | 'overdue';

export interface Notification {
  id: number;
  message: string;
  notification_type: NotificationType;
  user_id: number;
  task_id: number;
  task_title?: string;
  is_read: boolean;
  created_at: string;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface NotificationGenerationResponse {
  message: string;
  notifications_created: Record<string, number>;
  total: number;
}