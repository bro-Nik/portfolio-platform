import { QueryClient } from '@tanstack/react-query';
import type { QueryClientConfig } from '@tanstack/react-query';

export const defaultQueryOptions = {
  retry: 1,
  staleTime: 5 * 60 * 1000,
  refetchOnWindowFocus: true,
  refetchOnReconnect: true,
};

export const createQueryClient = (queryDefaults?: QueryClientConfig['defaultOptions']): QueryClient =>
  new QueryClient({
    defaultOptions: {
      queries: {
        ...defaultQueryOptions,
        ...queryDefaults?.queries,
      },
      mutations: queryDefaults?.mutations,
    },
  });
