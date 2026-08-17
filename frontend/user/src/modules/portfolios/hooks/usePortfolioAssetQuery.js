import { useQuery } from '@tanstack/react-query';
import { portfolioApi } from '../api/portfolioApi';

export const usePortfolioAssetTransactionsQuery = (portfolioId, assetId, options = {}) => {
  return useQuery({
    queryKey: ['portfolioAssetTransactions', portfolioId, assetId],
    queryFn: () => portfolioApi.getAssetTransactions(portfolioId, assetId),
    enabled: !!portfolioId && !!assetId,
    ...options,
  });
};
