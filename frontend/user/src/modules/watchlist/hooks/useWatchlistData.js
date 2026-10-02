import { useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWatchlistQuery } from './useWatchlistQuery';
import { useTickerIds } from 'src/hooks/TickerContext';
import { isTriggered } from '../utils/alerts';

export const useWatchlistData = (showArchived = false) => {
  const queryClient = useQueryClient();
  const { addTickerIds } = useTickerIds();
  const { data = [], isLoading } = useWatchlistQuery();

  useEffect(() => {
    const ids = (data || []).map(i => i.tickerId).filter(Boolean);
    if (ids.length > 0) addTickerIds(ids);
  }, [data, addTickerIds]);

  const filtered = useMemo(() => {
    if (showArchived) return data;
    const active = data.filter(i => !i.isArchived);
    return active.length > 0 ? active : data.filter(i => i.isArchived);
  }, [data, showArchived]);

  const stats = useMemo(() => {
    const alerts = data.flatMap(i => i.alerts || []);
    return {
      totalItems: data.length,
      activeAlerts: alerts.filter(a => a.isActive && !a.isArchived).length,
      triggeredAlerts: alerts.filter(isTriggered).length,
    };
  }, [data]);

  const showingArchivedFallback = !showArchived && data.length > 0 && data.every(i => i.isArchived);

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ['watchlist'] });
  };

  return { items: filtered, allItems: data, stats, loading: isLoading, showingArchivedFallback, refresh };
};
