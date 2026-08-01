import { useMutation, useQueryClient } from '@tanstack/react-query';
import { walletApi } from '../api/walletApi';

export const useWalletMutations = () => {
  const queryClient = useQueryClient();

  const updateOverviewWallet = (old, serverWallet) => {
    if (!old?.wallets) return { ...old, wallets: [serverWallet] };
    const idx = old.wallets.findIndex(w => w.id === serverWallet.id);
    if (idx === -1) {
      return { ...old, wallets: [...old.wallets, serverWallet] };
    }
    const updated = [...old.wallets];
    updated[idx] = serverWallet;
    return { ...old, wallets: updated };
  };

  const editWallet = useMutation({
    mutationFn: (wallet) => walletApi.saveWallet(wallet),

    onMutate: async (wallet) => {
      if (!wallet.id) return {};
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = queryClient.getQueryData(['overview']);

      queryClient.setQueryData(['overview'], (old) => {
        if (!old?.wallets) return old;
        return {
          ...old,
          wallets: old.wallets.map(w =>
            w.id === wallet.id ? { ...w, ...wallet } : w
          ),
        };
      });

      return { previous };
    },

    onSuccess: (serverWallet) => {
      if (!serverWallet?.id) return;
      queryClient.setQueryData(['overview'], (old) =>
        updateOverviewWallet(old, serverWallet)
      );
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['overview'], context.previous);
      }
    },
  });

  const deleteWallet = useMutation({
    mutationFn: (wallet) => walletApi.deleteWallet(wallet.id),

    onMutate: async (wallet) => {
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = queryClient.getQueryData(['overview']);

      queryClient.setQueryData(['overview'], (old) => {
        if (!old?.wallets) return old;
        return {
          ...old,
          wallets: old.wallets.filter(w => w.id !== wallet.id),
        };
      });

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['overview'], context.previous);
      }
    },
  });

  const archiveWallet = useMutation({
    mutationFn: (walletId) => walletApi.archiveWallet(walletId),

    onMutate: async (walletId) => {
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = queryClient.getQueryData(['overview']);

      const updateFn = (old) => {
        if (!old?.wallets) return old;
        return {
          ...old,
          wallets: old.wallets.map(w =>
            w.id === walletId
              ? {
                  ...w,
                  isArchived: true,
                  assets: w.assets?.map(a => ({ ...a, isArchived: true })) ?? [],
                }
              : w
          ),
        };
      };
      queryClient.setQueryData(['overview'], updateFn);

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['overview'], context.previous);
      }
    },
  });

  const unarchiveWallet = useMutation({
    mutationFn: (walletId) => walletApi.unarchiveWallet(walletId),

    onMutate: async (walletId) => {
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = queryClient.getQueryData(['overview']);

      const updateFn = (old) => {
        if (!old?.wallets) return old;
        return {
          ...old,
          wallets: old.wallets.map(w =>
            w.id === walletId ? { ...w, isArchived: false } : w
          ),
        };
      };
      queryClient.setQueryData(['overview'], updateFn);

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['overview'], context.previous);
      }
    },
  });

  const archiveWalletAsset = useMutation({
    mutationFn: ({ walletId, assetId }) => walletApi.archiveWalletAsset(walletId, assetId),

    onMutate: async ({ walletId, assetId }) => {
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = queryClient.getQueryData(['overview']);

      const updateFn = (old) => {
        if (!old?.wallets) return old;
        return {
          ...old,
          wallets: old.wallets.map(w => {
            if (w.id !== walletId) return w;
            return {
              ...w,
              assets: w.assets.map(a =>
                a.id === assetId ? { ...a, isArchived: true } : a
              ),
            };
          }),
        };
      };
      queryClient.setQueryData(['overview'], updateFn);

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['overview'], context.previous);
      }
    },
  });

  const unarchiveWalletAsset = useMutation({
    mutationFn: ({ walletId, assetId }) => walletApi.unarchiveWalletAsset(walletId, assetId),

    onMutate: async ({ walletId, assetId }) => {
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = queryClient.getQueryData(['overview']);

      const updateFn = (old) => {
        if (!old?.wallets) return old;
        return {
          ...old,
          wallets: old.wallets.map(w => {
            if (w.id !== walletId) return w;
            return {
              ...w,
              assets: w.assets.map(a =>
                a.id === assetId ? { ...a, isArchived: false } : a
              ),
            };
          }),
        };
      };
      queryClient.setQueryData(['overview'], updateFn);

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['overview'], context.previous);
      }
    },
  });

  const deleteWalletAsset = useMutation({
    mutationFn: ({ walletId, assetId }) => walletApi.deleteWalletAsset(walletId, assetId),

    onMutate: async ({ walletId, assetId }) => {
      await queryClient.cancelQueries({ queryKey: ['overview'] });
      const previous = queryClient.getQueryData(['overview']);

      const updateFn = (old) => {
        if (!old?.wallets) return old;
        return {
          ...old,
          wallets: old.wallets.map(w => {
            if (w.id !== walletId) return w;
            return {
              ...w,
              assets: w.assets.filter(a => a.id !== assetId),
            };
          }),
        };
      };
      queryClient.setQueryData(['overview'], updateFn);

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['overview'], context.previous);
      }
    },
  });

  return { editWallet, deleteWallet, archiveWallet, unarchiveWallet, archiveWalletAsset, unarchiveWalletAsset, deleteWalletAsset };
};
