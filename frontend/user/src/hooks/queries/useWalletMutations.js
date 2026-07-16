import { useMutation, useQueryClient } from '@tanstack/react-query';
import { walletApi } from '../../modules/wallets/api/walletApi';

export const useWalletMutations = () => {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['wallets'] });
    queryClient.invalidateQueries({ queryKey: ['portfolios'] });
  };

  const editWallet = useMutation({
    mutationFn: (wallet) => walletApi.saveWallet(wallet),
    onSuccess: () => invalidate(),
  });

  const deleteWallet = useMutation({
    mutationFn: (wallet) => walletApi.deleteWallet(wallet.id),
    onSuccess: () => invalidate(),
  });

  return { editWallet, deleteWallet };
};
