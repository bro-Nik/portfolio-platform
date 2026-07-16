import { useQuery } from '@tanstack/react-query';
import { walletApi } from '../../modules/wallets/api/walletApi';

export const useWalletsQuery = () => {
  return useQuery({
    queryKey: ['wallets'],
    queryFn: () => walletApi.getAllWallets(),
    refetchOnWindowFocus: false,
  });
};
