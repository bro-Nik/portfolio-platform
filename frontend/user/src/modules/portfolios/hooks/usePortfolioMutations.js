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

    onMutate: async ({ portfolio, asset }) => {
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      const previous = queryClient.getQueryData(['portfolios']);

      queryClient.setQueryData(['portfolios'], (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p => {
            if (p.id !== portfolio.id) return p;
            const tempAsset = {
              id: `optimistic-${Date.now()}`,
              tickerId: asset.id,
              portfolioId: portfolio.id,
              quantity: 0,
              amount: 0,
              buyOrders: 0,
              sellOrders: 0,
              realizedProfit: 0,
              totalInvested: 0,
              tags: [],
            };
            return { ...p, assets: [...p.assets, tempAsset] };
          }),
        };
      });

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['portfolios'], context.previous);
      }
    },

    onSettled: () => invalidate(),
  });

  const deleteAsset = useMutation({
    mutationFn: ({ portfolio, asset }) =>
      portfolioApi.delAssetFromPortfolio(portfolio.id, asset.id),

    onMutate: async ({ portfolio, asset }) => {
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      const previous = queryClient.getQueryData(['portfolios']);

      queryClient.setQueryData(['portfolios'], (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p => {
            if (p.id !== portfolio.id) return p;
            return {
              ...p,
              assets: p.assets.filter(a => a.id !== asset.id),
            };
          }),
        };
      });

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['portfolios'], context.previous);
      }
    },

    onSettled: () => invalidate(),
  });

  return { editPortfolio, deletePortfolio, addAsset, deleteAsset };
};
