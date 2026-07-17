import { createApi } from '@portfolio/shared';

const api = createApi('/market/api/tickers', { useAuth: true });

export const assetApi = {
  getTickersByMarket: (market, search, page) => {
    const params = { market, page: page.toString() };
    if (search) params.search = search;
    return api.get('', { params });
  },
};
