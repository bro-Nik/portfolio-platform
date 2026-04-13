import { createApi } from '@shared';
import { CreateUserData, UpdateUserData, User } from '/app/src/types/user';

const baseUrl = `${process.env.REACT_APP_AUTH_SERVICE_URL}/admin/users`;
const api = createApi(baseUrl, { convertCase: true, useAuth: true });

export const usersApi = {
  getUsers: (): Promise<User[]> => {
    return api.get('/');
  },

  getUser: (id: number): Promise<User> => {
    return api.get(`/${id}`);
  },

  createUser: (data: CreateUserData): Promise<User> => {
    return api.post('/', data);
  },

  updateUser: (id: number, data: UpdateUserData): Promise<User> => {
    return api.put(`/${id}`, data);
  },

  deleteUser: (id: number): Promise<void> => {
    return api.del(`/${id}`);
  },

  updateUserStatus: (id: number, status: string): Promise<User> => {
    return api.put(`/${id}/status`, { status });
  },

  fullLogoutUser: (id: number): Promise<void> => {
    return api.post('/logout-all', { userId: id });
  },

  bulkDeleteUsers: (ids: number[]): Promise<void> => {
    return api.post('/bulk-delete', { userIds: ids });
  },
};
