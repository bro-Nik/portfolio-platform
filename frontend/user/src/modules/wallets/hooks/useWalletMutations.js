import { useMutation, useQueryClient } from '@tanstack/react-query';
import { walletApi } from '../api/walletApi';

export const useWalletMutations = () => {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['wallets'] });
    queryClient.invalidateQueries({ queryKey: ['portfolios'] });
    queryClient.invalidateQueries({ queryKey: ['overview'] });
  };

  const editWallet = useMutation({
    mutationFn: (wallet) => walletApi.saveWallet(wallet),
    onSuccess: () => invalidate(),
  });

  const deleteWallet = useMutation({
    mutationFn: (wallet) => walletApi.deleteWallet(wallet.id),

    onMutate: async (wallet) => {
      await queryClient.cancelQueries({ queryKey: ['wallets'] });
      const previous = queryClient.getQueryData(['wallets']);

      queryClient.setQueryData(['wallets'], (old) => {
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
        queryClient.setQueryData(['wallets'], context.previous);
      }
    },

    onSettled: () => invalidate(),
  });

  const archiveWallet = useMutation({
    mutationFn: (walletId) => walletApi.archiveWallet(walletId),

    onMutate: async (walletId) => {
      await queryClient.cancelQueries({ queryKey: ['wallets'] });
      const previous = queryClient.getQueryData(['wallets']);

      queryClient.setQueryData(['wallets'], (old) => {
        if (!old?.wallets) return old;
        return {
          ...old,
          wallets: old.wallets.map(w =>
            w.id === walletId ? { ...w, isArchived: true } : w
          ),
        };
      });

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['wallets'], context.previous);
      }
    },

    onSettled: () => invalidate(),
  });

  const unarchiveWallet = useMutation({
    mutationFn: (walletId) => walletApi.unarchiveWallet(walletId),

    onMutate: async (walletId) => {
      await queryClient.cancelQueries({ queryKey: ['wallets'] });
      const previous = queryClient.getQueryData(['wallets']);

      queryClient.setQueryData(['wallets'], (old) => {
        if (!old?.wallets) return old;
        return {
          ...old,
          wallets: old.wallets.map(w =>
            w.id === walletId ? { ...w, isArchived: false } : w
          ),
        };
      });

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['wallets'], context.previous);
      }
    },

    onSettled: () => invalidate(),
  });

  const archiveWalletAsset = useMutation({
    mutationFn: ({ walletId, assetId }) => walletApi.archiveWalletAsset(walletId, assetId),

    onMutate: async ({ walletId, assetId }) => {
      await queryClient.cancelQueries({ queryKey: ['wallets'] });
      const previous = queryClient.getQueryData(['wallets']);

      queryClient.setQueryData(['wallets'], (old) => {
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
      });

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['wallets'], context.previous);
      }
    },

    onSettled: () => invalidate(),
  });

  const unarchiveWalletAsset = useMutation({
    mutationFn: ({ walletId, assetId }) => walletApi.unarchiveWalletAsset(walletId, assetId),

    onMutate: async ({ walletId, assetId }) => {
      await queryClient.cancelQueries({ queryKey: ['wallets'] });
      const previous = queryClient.getQueryData(['wallets']);

      queryClient.setQueryData(['wallets'], (old) => {
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
      });

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['wallets'], context.previous);
      }
    },

    onSettled: () => invalidate(),
  });

  const deleteWalletAsset = useMutation({
    mutationFn: ({ walletId, assetId }) => walletApi.deleteWalletAsset(walletId, assetId),
    onSuccess: () => invalidate(),
  });

  return { editWallet, deleteWallet, archiveWallet, unarchiveWallet, archiveWalletAsset, unarchiveWalletAsset, deleteWalletAsset };
};
