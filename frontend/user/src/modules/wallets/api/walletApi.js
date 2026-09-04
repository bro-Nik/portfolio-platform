import { getPortfolios } from 'src/api';

const portfolios = getPortfolios();

export const walletApi = {
  saveWallet: (walletData) => {
    if (walletData.id) {
      return portfolios.updateWalletApiWalletsWalletIdPut(walletData.id, walletData);
    }
    return portfolios.createWalletApiWalletsPost(walletData);
  },
  deleteWallet: (walletId) => portfolios.deleteWalletApiWalletsWalletIdDelete(walletId),
  setWalletArchived: (walletId, isArchived) =>
    portfolios.setWalletArchivedApiWalletsWalletIdPatch(walletId, { isArchived }),
  getAssetTransactions: (walletId, assetId) =>
    portfolios.getWalletAssetTransactionsApiWalletsWalletIdAssetsAssetIdTransactionsGet(walletId, assetId),
  setWalletAssetArchived: (walletId, assetId, isArchived) =>
    portfolios.setWalletAssetArchivedApiWalletsWalletIdAssetsAssetIdPatch(walletId, assetId, { isArchived }),
  deleteWalletAsset: (walletId, assetId) =>
    portfolios.deleteWalletAssetApiWalletsWalletIdAssetsAssetIdDelete(walletId, assetId),
};
