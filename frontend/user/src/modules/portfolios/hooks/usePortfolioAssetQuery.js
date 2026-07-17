import { useQuery } from '@tanstack/react-query';
import { portfolioApi } from '../api/portfolioApi';

export const usePortfolioAssetTransactionsQuery = (assetId, options = {}) => {
  return useQuery({
    queryKey: ['portfolioAssetTransactions', assetId],
    queryFn: () => portfolioApi.getAssetTransactions(assetId),
    enabled: !!assetId,
    ...options,
  });
};
