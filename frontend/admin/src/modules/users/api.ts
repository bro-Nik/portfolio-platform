import { getAuth } from 'src/api';
import type { UserCreateRequest, UserResponse, UserUpdateRequest } from 'src/api';

const auth = getAuth();

export const usersApi = {
  getUsers: (): Promise<UserResponse[]> => auth.getUsersAuthAdminUsersGet(),

  getUser: (id: number): Promise<UserResponse> => auth.getUserAuthAdminUsersUserIdGet(id),

  createUser: (data: UserCreateRequest): Promise<UserResponse> => auth.createUserAuthAdminUsersPost(data),

  updateUser: (id: number, data: UserUpdateRequest): Promise<UserResponse> =>
    auth.updateUserAuthAdminUsersUserIdPut(id, data),

  deleteUser: (id: number): Promise<void> => auth.deleteUserAuthAdminUsersUserIdDelete(id),

  updateUserStatus: (id: number, status: string): Promise<UserResponse> =>
    auth.updateUserAuthAdminUsersUserIdPut(id, { status }),

  fullLogoutUser: (id: number): Promise<void> => auth.logoutAllUserAuthAdminUsersUserIdLogoutAllPost(id),
};
