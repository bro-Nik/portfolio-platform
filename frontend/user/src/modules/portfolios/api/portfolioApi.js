import { apiService } from '/app/src/services/api';
import { authService } from '/app/src/services/auth';

const { getValidToken } = authService();
const api = apiService('/api/portfolios', getValidToken);

export const portfolioApi = {
  getPortfolios: (ids = null) => {
    const params = ids ? { ids } : {};
    return api.get('', { params });
  },
  savePortfolio: (portfolioData) => {
    if (portfolioData.id) {
      // Редактирование
      return api.put(`/${portfolioData.id}`, portfolioData);
    } else {
      // Создание
      return api.post('', portfolioData);
    }
  },
  deletePortfolio: (portfolioId) => api.del(`/${portfolioId}`),
  // getAsset: (assetId) => api.get(`/assets/${assetId}`),
  getAssetTransactions: (assetId) => api.get(`/assets/${assetId}/transactions`),
  addAssetToPortfolio: (portfolioId, tickerId) => api.post(`/${portfolioId}/assets`, {ticker_id: tickerId, portfolio_id: portfolioId}),
  delAssetFromPortfolio: (portfolioId, assetId) => api.del(`/${portfolioId}/assets/${assetId}`),
};
