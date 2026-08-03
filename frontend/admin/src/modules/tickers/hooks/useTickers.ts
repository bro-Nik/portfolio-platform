import { useQuery } from '@tanstack/react-query';
import { tickersApi } from '../api';

export const useTickers = (params: { search?: string; markets?: string[]; page?: number; pageSize?: number }) => {
  return useQuery({
    queryKey: ['tickers', params],
    queryFn: () => tickersApi.list(params),
  });
};

export const useTickerDetail = (id: number | null) => {
  return useQuery({
    queryKey: ['ticker', id],
    queryFn: () => tickersApi.getById(id!),
    enabled: id !== null,
  });
};
