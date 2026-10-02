import { useMutation, useQueryClient } from '@tanstack/react-query';
import { reconcileWatchlist } from '@portfolio/shared';
import { watchlistApi } from '../api/watchlistApi';

const snapshotWatchlist = async (queryClient) => {
  await queryClient.cancelQueries({ queryKey: ['watchlist'] });
  return queryClient.getQueryData(['watchlist']);
};

const rollbackWatchlist = (queryClient, previous) => {
  queryClient.setQueryData(['watchlist'], previous);
};

const invalidateWatchlist = (queryClient) => reconcileWatchlist(queryClient);

const replaceItem = (items, item) => {
  if (!items) return items;
  const idx = items.findIndex(i => i.id === item.id);
  if (idx === -1) return [...items, item];
  const updated = [...items];
  updated[idx] = item;
  return updated;
};

export const useWatchlistMutations = () => {
  const queryClient = useQueryClient();

  const addItem = useMutation({
    mutationFn: ({ ticker, comment }) => watchlistApi.addItem(ticker.id, comment),
    onMutate: async ({ ticker, comment }) => {
      const previous = await snapshotWatchlist(queryClient);
      const tempId = `temp-${Date.now()}`;
      queryClient.setQueryData(['watchlist'], (old) => [
        ...(old || []),
        {
          id: tempId,
          tickerId: ticker.id,
          name: ticker.name,
          symbol: ticker.symbol,
          image: ticker.image,
          market: ticker.market,
          price: ticker.price,
          comment,
          alerts: [],
          isArchived: false,
        },
      ]);
      return { previous, tempId };
    },
    onSuccess: (item, _vars, context) => {
      queryClient.setQueryData(['watchlist'], (old) =>
        old ? old.map(i => (i.id === context?.tempId ? item : i)) : [item]
      );
    },
    onError: (_e, _v, context) => rollbackWatchlist(queryClient, context?.previous),
    onSettled: () => invalidateWatchlist(queryClient),
  });

  const editItem = useMutation({
    mutationFn: ({ id, comment }) => watchlistApi.updateItem(id, comment),
    onMutate: async ({ id, comment }) => {
      const previous = await snapshotWatchlist(queryClient);
      queryClient.setQueryData(['watchlist'], (old) =>
        old?.map(i => (i.id === id ? { ...i, comment } : i))
      );
      return previous;
    },
    onSuccess: (item) => {
      queryClient.setQueryData(['watchlist'], (old) => (old ? replaceItem(old, item) : old));
    },
    onError: (_e, _v, previous) => rollbackWatchlist(queryClient, previous),
    onSettled: () => invalidateWatchlist(queryClient),
  });

  const deleteItem = useMutation({
    mutationFn: (id) => watchlistApi.deleteItem(id),
    onMutate: async (id) => {
      const previous = await snapshotWatchlist(queryClient);
      queryClient.setQueryData(['watchlist'], (old) => old?.filter(i => i.id !== id));
      return previous;
    },
    onError: (_e, _v, previous) => rollbackWatchlist(queryClient, previous),
    onSettled: () => invalidateWatchlist(queryClient),
  });

  const archiveItem = useMutation({
    mutationFn: ({ id, isArchived }) => watchlistApi.archiveItem(id, isArchived),
    onMutate: async ({ id, isArchived }) => {
      const previous = await snapshotWatchlist(queryClient);
      queryClient.setQueryData(['watchlist'], (old) =>
        old?.map(i => (i.id === id ? { ...i, isArchived } : i))
      );
      return previous;
    },
    onError: (_e, _v, previous) => rollbackWatchlist(queryClient, previous),
    onSettled: () => invalidateWatchlist(queryClient),
  });

  const saveAlert = useMutation({
    mutationFn: ({ itemId, alert, data }) =>
      typeof alert?.id === 'number'
        ? watchlistApi.updateAlert(alert.id, data)
        : watchlistApi.createAlert(itemId, data),
    onMutate: async ({ itemId, alert, data }) => {
      const previous = await snapshotWatchlist(queryClient);
      let tempId = null;
      queryClient.setQueryData(['watchlist'], (old) =>
        old?.map(i => {
          if (i.id !== itemId || !i.alerts) return i;
          if (typeof alert?.id === 'number') {
            return { ...i, alerts: i.alerts.map(a => (a.id === alert.id ? { ...a, ...data } : a)) };
          }
          tempId = `temp-alert-${Date.now()}`;
          return { ...i, alerts: [...i.alerts, { id: tempId, watchlistItemId: itemId, isActive: true, isArchived: false, ...data }] };
        })
      );
      return { previous, tempId, itemId };
    },
    onSuccess: (serverAlert, _vars, context) => {
      if (!context?.tempId) return;
      queryClient.setQueryData(['watchlist'], (old) =>
        old?.map(i => (i.id === context.itemId && i.alerts
          ? { ...i, alerts: i.alerts.map(a => (a.id === context.tempId ? serverAlert : a)) }
          : i))
      );
    },
    onError: (_e, _v, context) => rollbackWatchlist(queryClient, context?.previous),
    onSettled: () => invalidateWatchlist(queryClient),
  });

  const deleteAlert = useMutation({
    mutationFn: (alertId) => watchlistApi.deleteAlert(alertId),
    onMutate: async (alertId) => {
      const previous = await snapshotWatchlist(queryClient);
      queryClient.setQueryData(['watchlist'], (old) =>
        old?.map(i => (i.alerts ? { ...i, alerts: i.alerts.filter(a => a.id !== alertId) } : i))
      );
      return previous;
    },
    onError: (_e, _v, previous) => rollbackWatchlist(queryClient, previous),
    onSettled: () => invalidateWatchlist(queryClient),
  });

  const toggleAlert = useMutation({
    mutationFn: ({ alertId, isActive }) => watchlistApi.updateAlert(alertId, { isActive }),
    onMutate: async ({ alertId, isActive }) => {
      const previous = await snapshotWatchlist(queryClient);
      queryClient.setQueryData(['watchlist'], (old) =>
        old?.map(i => (i.alerts
          ? { ...i, alerts: i.alerts.map(a => (a.id === alertId ? { ...a, isActive } : a)) }
          : i))
      );
      return previous;
    },
    onError: (_e, _v, previous) => rollbackWatchlist(queryClient, previous),
    onSettled: () => invalidateWatchlist(queryClient),
  });

  return { addItem, editItem, deleteItem, archiveItem, saveAlert, deleteAlert, toggleAlert };
};
