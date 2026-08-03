import { createApi } from '@portfolio/shared';

const api = createApi('/market/api/tickers', { useAuth: true });

export const assetApi = {
  getTickersByMarket: (markets, search, page) => {
    const params = { markets, page: page.toString() };
    if (search) params.search = search;
    return api.get('', {
      params,
      paramsSerializer: { indexes: null },
    });
  },
};
