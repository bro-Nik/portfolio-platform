import { createApi } from '@portfolio/shared';

const api = createApi('/market/api/tickers', { useAuth: true });

export const assetApi = {
  getTickersByMarket: (markets, search, page, pageSize = 20) => {
    const params = { markets, page: page.toString(), page_size: pageSize.toString() };
    if (search) params.search = search;
    return api.get('', {
      params,
      paramsSerializer: { indexes: null },
    });
  },
};
