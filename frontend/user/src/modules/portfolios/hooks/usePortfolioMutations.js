import { useMutation, useQueryClient } from '@tanstack/react-query';
import { portfolioApi } from '../api/portfolioApi';

export const usePortfolioMutations = () => {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['portfolios'] });
    queryClient.invalidateQueries({ queryKey: ['wallets'] });
  };

  const editPortfolio = useMutation({
    mutationFn: (portfolio) => portfolioApi.savePortfolio(portfolio),
    onSuccess: () => invalidate(),
  });

  const deletePortfolio = useMutation({
    mutationFn: (portfolio) => portfolioApi.deletePortfolio(portfolio.id),
    onSuccess: () => invalidate(),
  });

  const addAsset = useMutation({
    mutationFn: ({ portfolio, asset }) =>
      portfolioApi.addAssetToPortfolio(portfolio.id, asset.id),
    onSuccess: () => invalidate(),
  });

  const deleteAsset = useMutation({
    mutationFn: ({ portfolio, asset }) =>
      portfolioApi.delAssetFromPortfolio(portfolio.id, asset.id),
    onSuccess: () => invalidate(),
  });

  return { editPortfolio, deletePortfolio, addAsset, deleteAsset };
};
