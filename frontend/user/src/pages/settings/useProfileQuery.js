import { useQuery } from '@tanstack/react-query';
import { settingsApi } from './settingsApi';

export const useProfileQuery = (options = {}) => {
  return useQuery({
    queryKey: ['profile'],
    queryFn: () => settingsApi.getProfile(),
    refetchOnWindowFocus: false,
    ...options,
  });
};
