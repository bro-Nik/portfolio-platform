import { useMutation, useQueryClient } from '@tanstack/react-query';
import { providersApi } from '../api';
import { CreateProviderData, Provider, UpdateProviderData } from '../../../../types/provider';
import { useNotifications } from '@portfolio/shared';

export const useProviderActions = () => {
  const queryClient = useQueryClient();
  const { error, success } = useNotifications();

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['providers'] });

  const simpleMutation = (successMsg: string, errorMsg: string) => ({
    onSuccess: () => {
      success(successMsg);
      invalidate();
    },
    onError: (err: Error) => error(err?.message || errorMsg),
  });

  const createMut = useMutation({
    mutationFn: (data: CreateProviderData) => providersApi.createProvider(data),
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: ['providers'] });
      const previous = queryClient.getQueryData<Provider[]>(['providers']);
      const optimisticId = `optimistic-${Date.now()}`;
      queryClient.setQueryData<Provider[]>(['providers'], (old: Provider[] | undefined) => [
        ...(old || []),
        { ...data, id: optimisticId } as unknown as Provider,
      ]);
      return { previous, optimisticId };
    },
    onSuccess: () => {
      success('API провайдер успешно создан');
    },
    onError: (err: Error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['providers'], context.previous);
      }
      error(err?.message || 'Ошибка создания');
    },
    onSettled: () => invalidate(),
  });

  const updateMut = useMutation({
    mutationFn: ({ name, data }: { name: string; data: UpdateProviderData }) =>
      providersApi.updateProvider(name, data),
    onMutate: async ({ name, data }) => {
      await queryClient.cancelQueries({ queryKey: ['providers'] });
      const previous = queryClient.getQueryData<Provider[]>(['providers']);
      queryClient.setQueryData<Provider[]>(['providers'], (old: Provider[] | undefined) =>
        old?.map((p: Provider) => p.name === name ? { ...p, ...data } : p)
      );
      return { previous };
    },
    onSuccess: (serverProvider, { name }) => {
      queryClient.setQueryData<Provider[]>(['providers'], (old: Provider[] | undefined) =>
        old?.map((p: Provider) => p.name === name ? serverProvider : p)
      );
      success('API провайдер обновлен');
    },
    onError: (err: Error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['providers'], context.previous);
      }
      error(err?.message || 'Ошибка обновления');
    },
  });

  const deleteMut = useMutation({
    mutationFn: (name: string) => providersApi.deleteProvider(name),
    onMutate: async (name) => {
      await queryClient.cancelQueries({ queryKey: ['providers'] });
      const previous = queryClient.getQueryData<Provider[]>(['providers']);
      queryClient.setQueryData<Provider[]>(['providers'], (old: Provider[] | undefined) =>
        old?.filter((p: Provider) => p.name !== name)
      );
      return { previous };
    },
    onSuccess: () => success('API провайдер удален'),
    onError: (err: Error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['providers'], context.previous);
      }
      error(err?.message || 'Ошибка удаления');
    },
  });

  const resetMut = useMutation({
    mutationFn: (name: string) => providersApi.resetCountersProvider(name),
    ...simpleMutation('Счетчики сброшены', 'Ошибка сброса'),
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
