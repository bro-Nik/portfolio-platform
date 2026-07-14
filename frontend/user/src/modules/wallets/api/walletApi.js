import { apiService } from '/app/src/services/api';
import { authService } from '/app/src/services/auth';

const { getValidToken } = authService();
const api = apiService('/api/wallets', getValidToken);

export const walletApi = {
  getAllWallets: () => api.get(''),
  saveWallet: (walletData) => {
    if (walletData.id) {
      // Редактирование
      return api.put(`/${walletData.id}`, walletData);
    } else {
      // Создание
      return api.post('', walletData);
    }
  },
  deleteWallet: (walletId) => api.del(`/${walletId}`),
  // getAsset: (assetId) => api.get(`/assets/${assetId}`),
  getAssetTransactions: (assetId) => api.get(`/assets/${assetId}/transactions`),
};
