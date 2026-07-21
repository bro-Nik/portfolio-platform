import { useMutation, useQueryClient } from '@tanstack/react-query';
import { providersApi } from '../api';
import { CreateProviderData, UpdateProviderData } from '../../../../types/provider';
import { useNotifications } from '@portfolio/shared';

export const useProviderActions = () => {
  const queryClient = useQueryClient();
  const { error, success } = useNotifications();

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['providers'] });

  // Общая логика для всех мутаций
  const mutationOptions = (successMsg: string, errorMsg: string) => ({
    onSuccess: () => {
      success(successMsg);
      invalidate();
    },
    onError: (err: Error) => error(err?.message || errorMsg),
  });

  const createMut = useMutation({
    mutationFn: (data: CreateProviderData) => providersApi.createProvider(data),
    ...mutationOptions('API провайдер успешно создан', 'Ошибка создания'),
  });

  const updateMut = useMutation({
    mutationFn: ({ name, data }: { name: string; data: UpdateProviderData }) => providersApi.updateProvider(name, data),
    ...mutationOptions('API провайдер обновлен', 'Ошибка обновления'),
  });

  const deleteMut = useMutation({
    mutationFn: (name: string) => providersApi.deleteProvider(name),
    ...mutationOptions('API провайдер удален', 'Ошибка удаления'),
  });

  const resetMut = useMutation({
    mutationFn: (name: string) => providersApi.resetCountersProvider(name),
    ...mutationOptions('Счетчики сброшены', 'Ошибка сброса'),
  });

  return {
    createProvider: (data: CreateProviderData) => createMut.mutate(data),
    updateProvider: (name: string, data: UpdateProviderData) => updateMut.mutate({ name, data }),
    deleteProvider: (name: string) => deleteMut.mutate(name),
    resetProviderCounters: (name: string) => resetMut.mutate(name),
    isCreating: createMut.isPending,
    isUpdating: updateMut.isPending,
    isDeleting: deleteMut.isPending,
    isResetting: resetMut.isPending,
  };
};
