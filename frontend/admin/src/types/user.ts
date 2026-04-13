export interface UserSession {
  id: number;
  userId: number;
  ipAddress: string;
  browser: string;
  os: string;
  lastActivityAt: string;
  createdAt: string;
}

export interface User {
  id: number;
  email: string;
  fullName?: string;
  role: string;
  status: string;
  isActive?: boolean;
  online?: boolean;
  lastActiveAt?: string;
  totalActiveTime?: number;
  createdAt: string;
  updatedAt?: string;
  loginSessions?: UserSession[];
}

export interface UserStats {
  total: number;
  active: number;
  online: number;
  admins: number;
  newMonth: number;
}

export interface UserFormData {
  email: string;
  password?: string;
  fullName?: string;
  role: string;
  status?: string;
}

export type CreateUserData = UserFormData;
export type UpdateUserData = Partial<UserFormData>;

export interface UserFilters {
  status: string;
  role: string;
}
