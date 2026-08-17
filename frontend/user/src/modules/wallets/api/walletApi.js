import { createApi } from '@portfolio/shared';

const api = createApi('/api/wallets', { useAuth: true });

export const walletApi = {
  saveWallet: (walletData) => {
    if (walletData.id) {
      return api.put(`/${walletData.id}`, walletData);
    } else {
      return api.post('', walletData);
    }
  },
  deleteWallet: (walletId) => api.del(`/${walletId}`),
  setWalletArchived: (walletId, isArchived) => api.patch(`/${walletId}`, { isArchived }),
  getAssetTransactions: (walletId, assetId) => api.get(`/${walletId}/assets/${assetId}/transactions`),
  setWalletAssetArchived: (walletId, assetId, isArchived) => api.patch(`/${walletId}/assets/${assetId}`, { isArchived }),
  deleteWalletAsset: (walletId, assetId) => api.del(`/${walletId}/assets/${assetId}`),
};
