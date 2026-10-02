import { useQuery } from '@tanstack/react-query';
import { watchlistApi } from '../api/watchlistApi';

export const useWatchlistQuery = () => {
  return useQuery({
    queryKey: ['watchlist'],
    queryFn: async () => {
      const data = await watchlistApi.getWatchlist();
      return data.items || [];
    },
    refetchOnWindowFocus: false,
  });
};
