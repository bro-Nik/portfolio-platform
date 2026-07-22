import { useMutation, useQueryClient } from '@tanstack/react-query';
import { tickersApi } from '../api';
import { TickerUpdateData } from '../../../types/ticker';
import { useNotifications } from '@portfolio/shared';

export const useTickerActions = () => {
  const queryClient = useQueryClient();
  const { error, success } = useNotifications();

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['tickers'] });

  const mutationOptions = (successMsg: string, errorMsg: string) => ({
    onSuccess: () => {
      success(successMsg);
      invalidate();
    },
    onError: (err: Error) => error(err?.message || errorMsg),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: TickerUpdateData }) => tickersApi.update(id, data),
    ...mutationOptions('Тикер обновлён', 'Ошибка обновления'),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => tickersApi.delete(id),
    ...mutationOptions('Тикер удалён', 'Ошибка удаления'),
  });

  const mergeMut = useMutation({
    mutationFn: ({ sourceId, targetId }: { sourceId: number; targetId: number }) => tickersApi.merge(sourceId, targetId),
    ...mutationOptions('Тикеры объединены', 'Ошибка слияния'),
  });

  return {
    updateTicker: (id: number, data: TickerUpdateData) => updateMut.mutate({ id, data }),
    deleteTicker: (id: number) => deleteMut.mutate(id),
    mergeTickers: (sourceId: number, targetId: number) => mergeMut.mutate({ sourceId, targetId }),
    isUpdating: updateMut.isPending,
    isDeleting: deleteMut.isPending,
    isMerging: mergeMut.isPending,
  };
};
