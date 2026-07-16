import { createApi } from '@portfolio/shared';

const api = createApi('/market/api/tickers', { useAuth: true });

export const assetApi = {
  getTickersByMarket: (market, search, page) => {
    const params = new URLSearchParams({ market, page: page.toString(), });
    if (search) params.append('search', search);
    return api.get(`?${params}`);
  },
};
