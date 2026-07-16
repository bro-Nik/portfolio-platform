import { useMutation, useQueryClient } from '@tanstack/react-query';
import { providersApi } from '../api';
import { CreateProviderData, UpdateProviderData } from '../../../../types/provider';
import { errorNotification, successNotification } from '../../../../utils';

export const useProviderActions = () => {
  const queryClient = useQueryClient();

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['providers'] });

  // Общая логика для всех мутаций
  const mutationOptions = (successMsg: string, errorMsg: string) => ({
    onSuccess: () => {
      successNotification(successMsg);
      invalidate();
    },
    onError: (error: Error) => errorNotification(error, errorMsg),
  });

  const createMut = useMutation({
    mutationFn: (data: CreateProviderData) => providersApi.createProvider(data),
    ...mutationOptions('API провайдер успешно создан', 'Ошибка создания'),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateProviderData }) => providersApi.updateProvider(id, data),
    ...mutationOptions('API провайдер обновлен', 'Ошибка обновления'),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => providersApi.deleteProvider(id),
    ...mutationOptions('API провайдер удален', 'Ошибка удаления'),
  });

  const resetMut = useMutation({
    mutationFn: (id: number) => providersApi.resetCountersProvider(id),
    ...mutationOptions('Счетчики сброшены', 'Ошибка сброса'),
  });

  return {
    createProvider: (data: CreateProviderData) => createMut.mutate(data),
    updateProvider: (id: number, data: UpdateProviderData) => updateMut.mutate({ id, data }),
    deleteProvider: (id: number) => deleteMut.mutate(id),
    resetProviderCounters: (id: number) => resetMut.mutate(id),
    isCreating: createMut.isPending,
    isUpdating: updateMut.isPending,
    isDeleting: deleteMut.isPending,
    isResetting: resetMut.isPending,
  };
};
