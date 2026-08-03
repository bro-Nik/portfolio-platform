import { createApi } from '@portfolio/shared';
import { Ticker, TickerListResponse, TickerUpdateData } from '../../types/ticker';

const baseUrl = `${import.meta.env.VITE_MARKET_SERVICE_URL}/admin/tickers`;
const api = createApi(baseUrl, { useAuth: true });

export const tickersApi = {
  list: (params: { search?: string; markets?: string[]; page?: number; pageSize?: number }): Promise<TickerListResponse> => {
    const queryParams: Record<string, string | number | string[]> = {};
    if (params.search) queryParams.search = params.search;
    if (params.markets?.length) queryParams.markets = params.markets;
    if (params.page) queryParams.page = params.page;
    if (params.pageSize) queryParams.page_size = params.pageSize;
    return api.get('', { params: queryParams, paramsSerializer: { indexes: null } });
  },

  getById: (id: number): Promise<Ticker> => {
    return api.get(`/${id}`);
  },

  update: (id: number, data: TickerUpdateData): Promise<Ticker> => {
    return api.put(`/${id}`, data);
  },

  delete: (id: number): Promise<void> => {
    return api.del(`/${id}`);
  },

  merge: (sourceId: number, targetId: number): Promise<Ticker> => {
    return api.post('/merge', { source_id: sourceId, target_id: targetId });
  },
};
