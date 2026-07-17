import { useState } from 'react';
import { transactionService } from 'src/modules/transaction/services/transactionService'
import { useTransactionMutations } from './useTransactionMutations';

export const useTransactionOperations = () => {
  const [loading, setLoading] = useState(false);

  const mutations = useTransactionMutations();

  const editTransaction = async (oldTransaction, newTransaction) => {
    const validation = transactionService.validateEdit(newTransaction);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }

    setLoading(true);
    try {
      const data = await mutations.saveTransaction.mutateAsync(newTransaction);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const deleteTransaction = async (transaction) => {
    const validation = transactionService.validateDelete(transaction);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }

    setLoading(true);
    try {
      const data = await mutations.deleteTransaction.mutateAsync(transaction);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  return {
    editTransaction,
    deleteTransaction,
    loading
  };
};
