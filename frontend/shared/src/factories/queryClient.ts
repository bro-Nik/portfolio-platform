import { QueryClient } from '@tanstack/react-query';
import type { QueryClientConfig } from '@tanstack/react-query';

export const defaultQueryOptions = {
  retry: 1,
  staleTime: 5 * 60 * 1000,
  // /api/overview дёргает всю БД по каждому переключению вкладки и сам
  // rate-limited до 10 запросов в минуту: каждое возвращение фокуса
  // превращалось в лишний поход на сервер.
  refetchOnWindowFocus: false,
  refetchOnReconnect: true,
};

/**
 * Повторять только сетевые и серверные ошибки.
 *
 * React Query по умолчанию повторяет и 4xx: получив 401 или 422, клиент
 * добросовестно повторял запрос, не соблюдая Retry-After.
 */
export const shouldRetryQuery = (failureCount: number, error: unknown): boolean => {
  if (failureCount >= 1) return false;
  const status = (error as { response?: { status?: number } })?.response?.status;
  if (status === undefined) return true;
  return status >= 500;
};

export const createQueryClient = (queryDefaults?: QueryClientConfig['defaultOptions']): QueryClient =>
  new QueryClient({
    defaultOptions: {
      queries: {
        ...defaultQueryOptions,
        retry: shouldRetryQuery,
        ...queryDefaults?.queries,
      },
      mutations: queryDefaults?.mutations,
    },
  });
