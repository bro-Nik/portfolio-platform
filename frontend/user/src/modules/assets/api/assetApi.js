import { createApi } from '@portfolio/shared';
import { API_BASE } from 'src/constants/api';

export const tickerApi = createApi(API_BASE.marketTickers, { useAuth: true });

export const assetApi = {
  getTickersByMarket: (markets, search, page, pageSize = 20) => {
    const params = { markets, page: page.toString(), page_size: pageSize.toString() };
    if (search) params.search = search;
    return tickerApi.get('', {
      params,
      paramsSerializer: { indexes: null },
    });
  },
};
