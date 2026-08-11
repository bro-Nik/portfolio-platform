import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { assetApi } from 'src/modules/assets/api/assetApi';
import { usePreferencesStore } from 'src/stores/preferencesStore';

export const useCurrencies = () => {
  const setRates = usePreferencesStore((state) => state.setRates);

  const query = useQuery({
    queryKey: ['currencies'],
    queryFn: async () => {
      const data = await assetApi.getTickersByMarket(['currency'], null, 1, 100);
      return data.data || [];
    },
    staleTime: 12 * 60 * 60 * 1000,
    refetchInterval: 12 * 60 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    const rates = (query.data || []).reduce((acc, ticker) => {
      if (ticker.symbol && typeof ticker.price === 'number') {
        acc[ticker.symbol] = ticker.price;
      }
      return acc;
    }, {});
    setRates(rates);
  }, [query.data, setRates]);

  return query;
};
