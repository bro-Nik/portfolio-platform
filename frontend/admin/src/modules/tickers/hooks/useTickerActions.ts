import { useMutation, useQueryClient } from '@tanstack/react-query';
import { tickersApi } from '../api';
import { Ticker, TickerListResponse, TickerUpdateData } from '../../../types/ticker';
import { useNotifications } from '@portfolio/shared';

export const useTickerActions = () => {
  const queryClient = useQueryClient();
  const { error, success } = useNotifications();

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['tickers'] });

  const snapshotTickers = () =>
    queryClient.getQueriesData<TickerListResponse>({ queryKey: ['tickers'] });

  const restoreSnapshot = (snapshot: ReturnType<typeof snapshotTickers>) => {
    snapshot.forEach(([key, data]) => {
      if (data) queryClient.setQueryData(key, data);
    });
  };

  const updateTickerInCache = (
    entries: ReturnType<typeof snapshotTickers>,
    id: number,
    updater: (t: Ticker) => Ticker
  ) => {
    entries.forEach(([key]) => {
      queryClient.setQueryData<TickerListResponse>(key, (old: TickerListResponse | undefined) => {
        if (!old?.data) return old;
        return { ...old, data: old.data.map((t: Ticker) => t.id === id ? updater(t) : t) };
      });
    });
  };

  const removeTickerFromCache = (
    entries: ReturnType<typeof snapshotTickers>,
    id: number
  ) => {
    entries.forEach(([key]) => {
      queryClient.setQueryData<TickerListResponse>(key, (old: TickerListResponse | undefined) => {
        if (!old?.data) return old;
        return { ...old, data: old.data.filter((t: Ticker) => t.id !== id), total: Math.max(0, (old.total || 0) - 1) };
      });
    });
  };

  const simpleMutation = (successMsg: string, errorMsg: string) => ({
    onSuccess: () => {
      success(successMsg);
      invalidate();
    },
    onError: (err: Error) => error(err?.message || errorMsg),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: TickerUpdateData }) => tickersApi.update(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: ['tickers'] });
      const snapshot = snapshotTickers();
      updateTickerInCache(snapshot, id, (t: Ticker) => ({ ...t, ...data }));
      return { snapshot };
    },
    onSuccess: (serverTicker, { id }) => {
      const entries = snapshotTickers();
      updateTickerInCache(entries, id, () => serverTicker);
      success('Тикер обновлён');
    },
    onError: (err: Error, _vars, context) => {
      if (context?.snapshot) restoreSnapshot(context.snapshot);
      error(err?.message || 'Ошибка обновления');
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => tickersApi.delete(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['tickers'] });
      const snapshot = snapshotTickers();
      removeTickerFromCache(snapshot, id);
      return { snapshot };
    },
    onSuccess: () => success('Тикер удалён'),
    onError: (err: Error, _vars, context) => {
      if (context?.snapshot) restoreSnapshot(context.snapshot);
      error(err?.message || 'Ошибка удаления');
    },
  });

  const mergeMut = useMutation({
    mutationFn: ({ sourceId, targetId }: { sourceId: number; targetId: number }) =>
      tickersApi.merge(sourceId, targetId),
    onMutate: async ({ sourceId, targetId }) => {
      await queryClient.cancelQueries({ queryKey: ['tickers'] });
      const snapshot = snapshotTickers();
      removeTickerFromCache(snapshot, sourceId);
      updateTickerInCache(snapshot, targetId, (t: Ticker) => ({ ...t }));
      return { snapshot, sourceId, targetId };
    },
    onSuccess: (serverTicker, { sourceId }, context) => {
      const entries = snapshotTickers();
      removeTickerFromCache(entries, sourceId);
      updateTickerInCache(entries, context.targetId, () => serverTicker);
      success('Тикеры объединены');
    },
    onError: (err: Error, _vars, context) => {
      if (context?.snapshot) restoreSnapshot(context.snapshot);
      error(err?.message || 'Ошибка слияния');
    },
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
