import { createApi } from '@portfolio/shared';

const api = createApi('/api/wallets', { useAuth: true });

export const walletApi = {
  getAllWallets: () => api.get(''),
  saveWallet: (walletData) => {
    if (walletData.id) {
      return api.put(`/${walletData.id}`, walletData);
    } else {
      return api.post('', walletData);
    }
  },
  deleteWallet: (walletId) => api.del(`/${walletId}`),
  archiveWallet: (walletId) => api.post(`/${walletId}/archive`),
  unarchiveWallet: (walletId) => api.post(`/${walletId}/unarchive`),
  getAssetTransactions: (assetId) => api.get(`/assets/${assetId}/transactions`),
  archiveWalletAsset: (walletId, assetId) => api.post(`/${walletId}/assets/${assetId}/archive`),
  unarchiveWalletAsset: (walletId, assetId) => api.post(`/${walletId}/assets/${assetId}/unarchive`),
  deleteWalletAsset: (walletId, assetId) => api.del(`/${walletId}/assets/${assetId}`),
};
