import { useMutation, useQueryClient } from '@tanstack/react-query';
import { reconcilePortfolioData, queryKeys } from '@portfolio/shared';
import { transactionApi } from '../api/transactionApi';

export const useTransactionMutations = () => {
  const queryClient = useQueryClient();

  const invalidate = () =>
    Promise.all([
      queryClient.invalidateQueries({ queryKey: queryKeys.overview }),
      queryClient.invalidateQueries({ queryKey: queryKeys.portfolioAssetTransactions }),
      queryClient.invalidateQueries({ queryKey: queryKeys.walletAssetTransactions }),
      queryClient.invalidateQueries({ queryKey: queryKeys.assetPrices }),
    ]);

  const saveTransaction = useMutation({
    mutationFn: (transaction) => transactionApi.saveTransaction(transaction),
    onSettled: () => reconcilePortfolioData(queryClient),
  });

  const deleteTransaction = useMutation({
    mutationFn: (transaction) => transactionApi.deleteTransaction(transaction.id),
    onSettled: () => reconcilePortfolioData(queryClient),
  });

  return { saveTransaction, deleteTransaction, invalidate };
};
