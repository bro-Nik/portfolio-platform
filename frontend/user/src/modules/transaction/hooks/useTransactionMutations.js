import { useMutation, useQueryClient } from '@tanstack/react-query';
import { reconcilePortfolioData } from '@portfolio/shared';
import { transactionApi } from '../api/transactionApi';

export const useTransactionMutations = () => {
  const queryClient = useQueryClient();

  const saveTransaction = useMutation({
    mutationFn: (transaction) => transactionApi.saveTransaction(transaction),
    onSettled: () => reconcilePortfolioData(queryClient),
  });

  const deleteTransaction = useMutation({
    mutationFn: (transaction) => transactionApi.deleteTransaction(transaction.id),
    onSettled: () => reconcilePortfolioData(queryClient),
  });

  return { saveTransaction, deleteTransaction };
};
