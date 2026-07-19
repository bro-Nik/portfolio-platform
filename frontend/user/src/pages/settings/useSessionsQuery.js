import { useQuery } from '@tanstack/react-query';
import { authService } from '@portfolio/shared';

export const useSessionsQuery = (options = {}) => {
  const { getSessions } = authService();

  return useQuery({
    queryKey: ['sessions'],
    queryFn: () => getSessions().then(res => res.success ? (res.data || []) : []),
    refetchOnWindowFocus: false,
    ...options,
  });
};
