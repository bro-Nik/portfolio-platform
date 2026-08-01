import { useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionApi } from '../api/transactionApi';

export const useTransactionMutations = () => {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['overview'] });
    queryClient.invalidateQueries({ queryKey: ['portfolioAssetTransactions'] });
    queryClient.invalidateQueries({ queryKey: ['walletAssetTransactions'] });
  };

  const saveTransaction = useMutation({
    mutationFn: (transaction) => transactionApi.saveTransaction(transaction),
    onSuccess: () => invalidate(),
  });

  const deleteTransaction = useMutation({
    mutationFn: (transaction) => transactionApi.deleteTransaction(transaction.id),
    onSuccess: () => invalidate(),
  });

  return { saveTransaction, deleteTransaction };
};
