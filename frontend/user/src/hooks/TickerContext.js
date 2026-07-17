import { createContext, useContext, useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { createApi } from '@portfolio/shared';

const TickerIdsContext = createContext(null);

const marketApi = createApi('/market/api/tickers', { useAuth: true });

export const TickerIdsProvider = ({ children }) => {
  const [tickerIds, setTickerIds] = useState([]);

  const addTickerIds = useCallback((ids) => {
    if (!ids || ids.length === 0) return;
    setTickerIds(prev => {
      const newIds = ids.filter(id => !prev.includes(id));
      if (newIds.length === 0) return prev;
      return [...prev, ...newIds];
    });
  }, []);

  return (
    <TickerIdsContext.Provider value={{ tickerIds, addTickerIds }}>
      {children}
    </TickerIdsContext.Provider>
  );
};

export const useTickerIds = () => {
  const ctx = useContext(TickerIdsContext);
  if (!ctx) throw new Error('useTickerIds must be used within TickerIdsProvider');
  return ctx;
};

export const useAssetPricesQuery = () => {
  const { tickerIds } = useTickerIds();

  return useQuery({
    queryKey: ['assetPrices', tickerIds],
    queryFn: () => marketApi.post('/prices', tickerIds),
    enabled: tickerIds.length > 0,
    refetchInterval: 12 * 60 * 60 * 1000,
    staleTime: 12 * 60 * 60 * 1000,
  });
};

export const extractTickerIds = (data) => {
  const ids = new Set();
  (data || []).forEach(item => {
    (item.assets || []).forEach(asset => {
      if (asset.tickerId) ids.add(asset.tickerId);
    });
  });
  return [...ids];
};
