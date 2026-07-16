import { useState } from 'react';
import { useDataStore } from 'src/stores/dataStore';
import { transactionService } from 'src/modules/transaction/services/transactionService'
import { transactionApi } from 'src/modules/transaction/api/transactionApi';

export const useTransactionOperations = () => {
  const [loading, setLoading] = useState(false);

  const updatePortfolioAssets = useDataStore(state => state.updatePortfolioAssets);
  const updateWalletAssets = useDataStore(state => state.updateWalletAssets);

  const editTransaction = async (oldTransaction, newTransaction) => {
    const validation = transactionService.validateEdit(newTransaction);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);
    try {
      const data = await transactionApi.saveTransaction(newTransaction);
      if (data.portfolioAssets) updatePortfolioAssets(data.portfolioAssets);
      if (data.walletAssets) updateWalletAssets(data.walletAssets);
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
      const data = await transactionApi.deleteTransaction(transaction.id);
      if (data.portfolioAssets) updatePortfolioAssets(data.portfolioAssets);
      if (data.walletAssets) updateWalletAssets(data.walletAssets);
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
