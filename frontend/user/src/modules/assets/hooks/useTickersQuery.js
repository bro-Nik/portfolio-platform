import { useInfiniteQuery } from '@tanstack/react-query';
import { assetApi } from 'src/modules/assets/api/assetApi';

export const useTickersQuery = (markets, search) => {
  return useInfiniteQuery({
    queryKey: ['tickers', markets, search],
    queryFn: ({ pageParam = 1 }) => assetApi.getTickersByMarket(markets, search, pageParam),
    getNextPageParam: (lastPage, allPages) => lastPage.hasMore ? allPages.length + 1 : undefined,
    enabled: !markets || markets.length > 0,
    refetchOnWindowFocus: false,
  });
};
