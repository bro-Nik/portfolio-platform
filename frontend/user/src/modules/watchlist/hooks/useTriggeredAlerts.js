import { useQuery } from '@tanstack/react-query';
import { watchlistApi } from '../api/watchlistApi';

export const useTriggeredAlerts = () => {
  return useQuery({
    queryKey: ['triggeredAlerts'],
    queryFn: async () => {
      const data = await watchlistApi.getTriggered();
      return data.alerts || [];
    },
    refetchInterval: 60 * 1000,
    refetchOnWindowFocus: false,
  });
};
