import { useInfiniteQuery } from '@tanstack/react-query';
import { assetApi } from 'src/modules/assets/api/assetApi';

export const useTickersQuery = (market, search) => {
  return useInfiniteQuery({
    queryKey: ['tickers', market, search],
    queryFn: ({ pageParam = 1 }) => assetApi.getTickersByMarket(market, search, pageParam),
    getNextPageParam: (lastPage, allPages) => lastPage.hasMore ? allPages.length + 1 : undefined,
    enabled: !!market,
    refetchOnWindowFocus: false,
  });
};
