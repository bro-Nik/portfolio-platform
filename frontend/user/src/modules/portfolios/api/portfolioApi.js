import { createApi } from '@portfolio/shared';

const api = createApi('/api/portfolios', { useAuth: true });

export const portfolioApi = {
  getPortfolios: (ids = null) => {
    const params = ids ? { ids } : {};
    return api.get('', { params });
  },
  savePortfolio: (portfolioData) => {
    if (portfolioData.id) {
      return api.put(`/${portfolioData.id}`, portfolioData);
    } else {
      return api.post('', portfolioData);
    }
  },
  deletePortfolio: (portfolioId) => api.del(`/${portfolioId}`),
  getAssetTransactions: (assetId) => api.get(`/assets/${assetId}/transactions`),
  addAssetToPortfolio: (portfolioId, tickerId) => api.post(`/${portfolioId}/assets`, {ticker_id: tickerId, portfolio_id: portfolioId}),
  delAssetFromPortfolio: (portfolioId, assetId) => api.del(`/${portfolioId}/assets/${assetId}`),
};
