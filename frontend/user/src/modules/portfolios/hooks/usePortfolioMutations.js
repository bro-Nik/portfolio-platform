import { useMutation, useQueryClient } from '@tanstack/react-query';
import { portfolioApi } from '../api/portfolioApi';

export const usePortfolioMutations = () => {
  const queryClient = useQueryClient();

  const updateOverviewPortfolio = (old, serverPortfolio) => {
    if (!old?.portfolios) return { ...old, portfolios: [serverPortfolio] };
    const idx = old.portfolios.findIndex(p => p.id === serverPortfolio.id);
    if (idx === -1) {
      return { ...old, portfolios: [...old.portfolios, serverPortfolio] };
    }
    const updated = [...old.portfolios];
    updated[idx] = serverPortfolio;
    return { ...old, portfolios: updated };
  };

  const updateCache = (old, serverPortfolio) => {
    if (!old?.portfolios) return { portfolios: [serverPortfolio] };
    const idx = old.portfolios.findIndex(p => p.id === serverPortfolio.id);
    if (idx === -1) {
      return { ...old, portfolios: [...old.portfolios, serverPortfolio] };
    }
    const updated = [...old.portfolios];
    updated[idx] = serverPortfolio;
    return { ...old, portfolios: updated };
  };

  const editPortfolio = useMutation({
    mutationFn: (portfolio) => portfolioApi.savePortfolio(portfolio),

    onMutate: async (portfolio) => {
      if (!portfolio.id) return {};
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = {
        portfolios: queryClient.getQueryData(['portfolios']),
        overview: queryClient.getQueryData(['overview']),
      };

      queryClient.setQueryData(['portfolios'], (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p =>
            p.id === portfolio.id ? { ...p, ...portfolio } : p
          ),
        };
      });

      return { previous };
    },

    onSuccess: (serverPortfolio) => {
      if (!serverPortfolio?.id) return;
      queryClient.setQueryData(['portfolios'], (old) =>
        updateCache(old, serverPortfolio)
      );
      queryClient.setQueryData(['overview'], (old) =>
        updateOverviewPortfolio(old, serverPortfolio)
      );
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['portfolios'], context.previous.portfolios);
        queryClient.setQueryData(['overview'], context.previous.overview);
      }
    },
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
  });

  const addAsset = useMutation({
    mutationFn: ({ portfolio, asset }) =>
      portfolioApi.addAssetToPortfolio(portfolio.id, asset.id),

    onMutate: async ({ portfolio, asset }) => {
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = {
        portfolios: queryClient.getQueryData(['portfolios']),
        overview: queryClient.getQueryData(['overview']),
      };

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
      const addTempAsset = (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p =>
            p.id !== portfolio.id ? p : { ...p, assets: [...p.assets, tempAsset] }
          ),
        };
      };
      queryClient.setQueryData(['portfolios'], addTempAsset);
      queryClient.setQueryData(['overview'], addTempAsset);

      return { previous };
    },

    onSuccess: (serverAsset) => {
      if (!serverAsset?.id) return;
      const replaceTemp = (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p => {
            if (p.id !== serverAsset.portfolioId) return p;
            return {
              ...p,
              assets: p.assets.map(a =>
                typeof a.id === 'string' && a.id.startsWith('optimistic-') ? serverAsset : a
              ),
            };
          }),
        };
      };
      queryClient.setQueryData(['portfolios'], replaceTemp);
      queryClient.setQueryData(['overview'], replaceTemp);
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['portfolios'], context.previous.portfolios);
        queryClient.setQueryData(['overview'], context.previous.overview);
      }
    },
  });

  const deleteAsset = useMutation({
    mutationFn: ({ portfolio, asset }) =>
      portfolioApi.delAssetFromPortfolio(portfolio.id, asset.id),

    onMutate: async ({ portfolio, asset }) => {
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = {
        portfolios: queryClient.getQueryData(['portfolios']),
        overview: queryClient.getQueryData(['overview']),
      };

      const updateFn = (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p => {
            if (p.id !== portfolio.id) return p;
            return { ...p, assets: p.assets.filter(a => a.id !== asset.id) };
          }),
        };
      };
      queryClient.setQueryData(['portfolios'], updateFn);
      queryClient.setQueryData(['overview'], updateFn);

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['portfolios'], context.previous.portfolios);
        queryClient.setQueryData(['overview'], context.previous.overview);
      }
    },
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
  });

  const archiveAsset = useMutation({
    mutationFn: ({ portfolioId, assetId }) => portfolioApi.archiveAsset(portfolioId, assetId),

    onMutate: async ({ portfolioId, assetId }) => {
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = {
        portfolios: queryClient.getQueryData(['portfolios']),
        overview: queryClient.getQueryData(['overview']),
      };

      const updateFn = (old) => {
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
      };
      queryClient.setQueryData(['portfolios'], updateFn);
      queryClient.setQueryData(['overview'], updateFn);

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['portfolios'], context.previous.portfolios);
        queryClient.setQueryData(['overview'], context.previous.overview);
      }
    },
  });

  const unarchiveAsset = useMutation({
    mutationFn: ({ portfolioId, assetId }) => portfolioApi.unarchiveAsset(portfolioId, assetId),

    onMutate: async ({ portfolioId, assetId }) => {
      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = {
        portfolios: queryClient.getQueryData(['portfolios']),
        overview: queryClient.getQueryData(['overview']),
      };

      const updateFn = (old) => {
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
      };
      queryClient.setQueryData(['portfolios'], updateFn);
      queryClient.setQueryData(['overview'], updateFn);

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['portfolios'], context.previous.portfolios);
        queryClient.setQueryData(['overview'], context.previous.overview);
      }
    },
  });

  return { editPortfolio, deletePortfolio, addAsset, deleteAsset, archivePortfolio, unarchivePortfolio, archiveAsset, unarchiveAsset };
};
