import { useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '../api';
import { CreateUserData, UpdateUserData, User } from '../../../types/user';
import type { UserCreateRequest as UserCreateRequestData, UserUpdateRequest as UserUpdateRequestData } from 'src/api';
import { useNotifications } from '@portfolio/shared';

export const useUserActions = () => {
  const queryClient = useQueryClient();
  const { error, success } = useNotifications();

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['users'] });

  const simpleMutation = (successMsg: string, errorMsg: string) => ({
    onSuccess: () => {
      success(successMsg);
      invalidate();
    },
    onError: (err: Error) => error(err?.message || errorMsg),
  });

  const createMut = useMutation({
    mutationFn: (data: CreateUserData) => usersApi.createUser(data as UserCreateRequestData),
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: ['users'] });
      const previous = queryClient.getQueryData<User[]>(['users']);
      const optimisticId = `optimistic-${Date.now()}`;
      queryClient.setQueryData<User[]>(['users'], (old: User[] | undefined) => [
        ...(old || []),
        { ...data, id: optimisticId } as unknown as User,
      ]);
      return { previous, optimisticId };
    },
    onSuccess: () => {
      success('Пользователь успешно создан');
    },
    onError: (err: Error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['users'], context.previous);
      }
      error(err?.message || 'Ошибка создания');
    },
    onSettled: () => invalidate(),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateUserData }) => usersApi.updateUser(id, data as UserUpdateRequestData),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: ['users'] });
      const previous = queryClient.getQueryData<User[]>(['users']);
      queryClient.setQueryData<User[]>(['users'], (old: User[] | undefined) =>
        old?.map((u: User) => u.id === id ? ({ ...u, ...data } as User) : u)
      );
      return { previous };
    },
    onSuccess: (serverUser, { id }) => {
      queryClient.setQueryData<User[]>(['users'], (old: User[] | undefined) =>
        old?.map((u: User) => u.id === id ? serverUser : u)
      );
      success('Данные пользователя обновлены');
    },
    onError: (err: Error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['users'], context.previous);
      }
      error(err?.message || 'Ошибка обновления');
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => usersApi.deleteUser(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['users'] });
      const previous = queryClient.getQueryData<User[]>(['users']);
      queryClient.setQueryData<User[]>(['users'], (old: User[] | undefined) =>
        old?.filter((u: User) => u.id !== id)
      );
      return { previous };
    },
    onSuccess: () => success('Пользователь удалён'),
    onError: (err: Error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['users'], context.previous);
      }
      error(err?.message || 'Ошибка удаления');
    },
  });

  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      usersApi.updateUserStatus(id, status),
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: ['users'] });
      const previous = queryClient.getQueryData<User[]>(['users']);
      queryClient.setQueryData<User[]>(['users'], (old: User[] | undefined) =>
        old?.map((u: User) => u.id === id ? { ...u, status } : u)
      );
      return { previous };
    },
    onSuccess: (serverUser, { id }) => {
      queryClient.setQueryData<User[]>(['users'], (old: User[] | undefined) =>
        old?.map((u: User) => u.id === id ? serverUser : u)
      );
      success('Статус пользователя обновлён');
    },
    onError: (err: Error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['users'], context.previous);
      }
      error(err?.message || 'Ошибка обновления статуса');
    },
  });

  const logoutMut = useMutation({
    mutationFn: (id: number) => usersApi.fullLogoutUser(id),
    ...simpleMutation('Выход из всех устройств выполнен', 'Ошибка выхода'),
  });

  return {
    createUser: (data: CreateUserData) => createMut.mutate(data),
    updateUser: (id: number, data: UpdateUserData) => updateMut.mutate({ id, data }),
    deleteUser: (id: number) => deleteMut.mutate(id),
    updateUserStatus: (id: number, status: string) => statusMut.mutate({ id, status }),
    logoutAllDevices: (id: number) => logoutMut.mutate(id),
    isCreating: createMut.isPending,
    isUpdating: updateMut.isPending,
    isDeleting: deleteMut.isPending,
    isUpdatingStatus: statusMut.isPending,
  };
};
