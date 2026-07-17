import { useQuery } from '@tanstack/react-query';
import { walletApi } from '../api/walletApi';

export const useWalletAssetTransactionsQuery = (assetId, options = {}) => {
  return useQuery({
    queryKey: ['walletAssetTransactions', assetId],
    queryFn: () => walletApi.getAssetTransactions(assetId),
    enabled: !!assetId,
    ...options,
  });
};
