export type {
  LoginSessionResponse as UserSession,
  UserResponse as User,
} from 'src/api';

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
