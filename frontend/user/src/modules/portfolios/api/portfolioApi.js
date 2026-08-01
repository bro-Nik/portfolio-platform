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
  archivePortfolio: (portfolioId) => api.post(`/${portfolioId}/archive`),
  unarchivePortfolio: (portfolioId) => api.post(`/${portfolioId}/unarchive`),
  getAssetTransactions: (assetId) => api.get(`/assets/${assetId}/transactions`),
  addAssetToPortfolio: (portfolioId, tickerId) => api.post(`/${portfolioId}/assets`, {ticker_id: tickerId, portfolio_id: portfolioId}),
  delAssetFromPortfolio: (portfolioId, assetId) => api.del(`/${portfolioId}/assets/${assetId}`),
  archiveAsset: (portfolioId, assetId) => api.post(`/${portfolioId}/assets/${assetId}/archive`),
  unarchiveAsset: (portfolioId, assetId) => api.post(`/${portfolioId}/assets/${assetId}/unarchive`),
};
