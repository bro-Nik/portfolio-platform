import { useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '../api';
import { CreateUserData, UpdateUserData } from '../../../types/user';
import { errorNotification, successNotification } from '../../../utils';

export const useUserActions = () => {
  const queryClient = useQueryClient();

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['users'] });

  const mutationOptions = (successMsg: string, errorMsg: string) => ({
    onSuccess: () => {
      successNotification(successMsg);
      invalidate();
    },
    onError: (error: Error) => errorNotification(error, errorMsg),
  });

  const createMut = useMutation({
    mutationFn: (data: CreateUserData) => usersApi.createUser(data),
    ...mutationOptions('Пользователь успешно создан', 'Ошибка создания'),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateUserData }) => usersApi.updateUser(id, data),
    ...mutationOptions('Данные пользователя обновлены', 'Ошибка обновления'),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => usersApi.deleteUser(id),
    ...mutationOptions('Пользователь удалён', 'Ошибка удаления'),
  });

  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => usersApi.updateUserStatus(id, status),
    ...mutationOptions('Статус пользователя обновлён', 'Ошибка обновления статуса'),
  });

  const logoutMut = useMutation({
    mutationFn: (id: number) => usersApi.fullLogoutUser(id),
    ...mutationOptions('Выход из всех устройств выполнен', 'Ошибка выхода'),
  });

  const bulkDeleteMut = useMutation({
    mutationFn: (ids: number[]) => usersApi.bulkDeleteUsers(ids),
    ...mutationOptions('Пользователи удалены', 'Ошибка массового удаления'),
  });

  return {
    createUser: (data: CreateUserData) => createMut.mutate(data),
    updateUser: (id: number, data: UpdateUserData) => updateMut.mutate({ id, data }),
    deleteUser: (id: number) => deleteMut.mutate(id),
    updateUserStatus: (id: number, status: string) => statusMut.mutate({ id, status }),
    logoutAllDevices: (id: number) => logoutMut.mutate(id),
    bulkDeleteUsers: (ids: number[]) => bulkDeleteMut.mutate(ids),
    isCreating: createMut.isPending,
    isUpdating: updateMut.isPending,
    isDeleting: deleteMut.isPending,
    isUpdatingStatus: statusMut.isPending,
    isBulkDeleting: bulkDeleteMut.isPending,
  };
};
