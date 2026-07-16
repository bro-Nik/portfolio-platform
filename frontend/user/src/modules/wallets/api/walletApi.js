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
  getAssetTransactions: (assetId) => api.get(`/assets/${assetId}/transactions`),
};
