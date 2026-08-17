import { createApi } from '@portfolio/shared';

const api = createApi('/api/portfolios', { useAuth: true });

export const portfolioApi = {
  savePortfolio: (portfolioData) => {
    if (portfolioData.id) {
      return api.put(`/${portfolioData.id}`, portfolioData);
    } else {
      return api.post('', portfolioData);
    }
  },
  deletePortfolio: (portfolioId) => api.del(`/${portfolioId}`),
  setPortfolioArchived: (portfolioId, isArchived) => api.patch(`/${portfolioId}`, { isArchived }),
  getAssetTransactions: (portfolioId, assetId) => api.get(`/${portfolioId}/assets/${assetId}/transactions`),
  addAssetToPortfolio: (portfolioId, tickerId) => api.post(`/${portfolioId}/assets`, {ticker_id: tickerId, portfolio_id: portfolioId}),
  delAssetFromPortfolio: (portfolioId, assetId) => api.del(`/${portfolioId}/assets/${assetId}`),
  setAssetArchived: (portfolioId, assetId, isArchived) => api.patch(`/${portfolioId}/assets/${assetId}`, { isArchived }),
};
