import { useMutation, useQueryClient } from '@tanstack/react-query';
import { portfolioApi } from '../api/portfolioApi';

export const usePortfolioMutations = () => {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['portfolios'] });
    queryClient.invalidateQueries({ queryKey: ['wallets'] });
    queryClient.invalidateQueries({ queryKey: ['overview'] });
  };

  const editPortfolio = useMutation({
    mutationFn: (portfolio) => portfolioApi.savePortfolio(portfolio),
    onSuccess: () => invalidate(),
  });

  const deletePortfolio = useMutation({
    mutationFn: (portfolio) => portfolioApi.deletePortfolio(portfolio.id),

    onMutate: async (portfolio) => {
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      const previous = queryClient.getQueryData(['portfolios']);

      queryClient.setQueryData(['portfolios'], (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.filter(p => p.id !== portfolio.id),
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

  const archivePortfolio = useMutation({
    mutationFn: (portfolioId) => portfolioApi.archivePortfolio(portfolioId),

    onMutate: async (portfolioId) => {
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      const previous = queryClient.getQueryData(['portfolios']);

      queryClient.setQueryData(['portfolios'], (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p =>
            p.id === portfolioId ? { ...p, isArchived: true } : p
          ),
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

  const unarchivePortfolio = useMutation({
    mutationFn: (portfolioId) => portfolioApi.unarchivePortfolio(portfolioId),

    onMutate: async (portfolioId) => {
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      const previous = queryClient.getQueryData(['portfolios']);

      queryClient.setQueryData(['portfolios'], (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p =>
            p.id === portfolioId ? { ...p, isArchived: false } : p
          ),
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

  const archiveAsset = useMutation({
    mutationFn: ({ portfolioId, assetId }) => portfolioApi.archiveAsset(portfolioId, assetId),

    onMutate: async ({ portfolioId, assetId }) => {
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      const previous = queryClient.getQueryData(['portfolios']);

      queryClient.setQueryData(['portfolios'], (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p => {
            if (p.id !== portfolioId) return p;
            return {
              ...p,
              assets: p.assets.map(a =>
                a.id === assetId ? { ...a, isArchived: true } : a
              ),
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

  const unarchiveAsset = useMutation({
    mutationFn: ({ portfolioId, assetId }) => portfolioApi.unarchiveAsset(portfolioId, assetId),

    onMutate: async ({ portfolioId, assetId }) => {
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      const previous = queryClient.getQueryData(['portfolios']);

      queryClient.setQueryData(['portfolios'], (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p => {
            if (p.id !== portfolioId) return p;
            return {
              ...p,
              assets: p.assets.map(a =>
                a.id === assetId ? { ...a, isArchived: false } : a
              ),
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

  return { editPortfolio, deletePortfolio, addAsset, deleteAsset, archivePortfolio, unarchivePortfolio, archiveAsset, unarchiveAsset };
};
