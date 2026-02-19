import { apiService } from '/app/src/services/api';
import { authService } from '/app/src/services/auth';

const { getValidToken } = authService();
const api = apiService('/market/api/tickers', getValidToken);

export const assetApi = {
  getTickersByMarket: (market, search, page) => {
    const params = new URLSearchParams({ market, page: page.toString(), });
    if (search) params.append('search', search);
    return api.get(`?${params}`);
  },
};
