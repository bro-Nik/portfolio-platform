import { useQuery } from '@tanstack/react-query';
import { walletApi } from '../api/walletApi';

export const useWalletAssetTransactionsQuery = (walletId, assetId, options = {}) => {
  return useQuery({
    queryKey: ['walletAssetTransactions', walletId, assetId],
    queryFn: () => walletApi.getAssetTransactions(walletId, assetId),
    enabled: !!walletId && !!assetId,
    ...options,
  });
};
