import { useState } from 'react';
import { useDataStore } from '/app/src/stores/dataStore';
import { transactionService } from '/app/src/modules/transaction/services/transactionService'
import { transactionApi } from '/app/src/modules/transaction/api/transactionApi';

export const useTransactionOperations = () => {
  const [loading, setLoading] = useState(false);

  const updatePortfolioAssets = useDataStore(state => state.updatePortfolioAssets);
  const updateWalletAssets = useDataStore(state => state.updateWalletAssets);

  const editTransaction = async (oldTransaction, newTransaction) => {
    // Валидация бизнес-правилами
    const validation = transactionService.validateEdit(newTransaction);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);

    // Вызов API
    const result = await transactionApi.saveTransaction(newTransaction);

    // Редактирование
    if (result.success) {

      // Обновление активов портфелей
      if (result.data.portfolioAssets) updatePortfolioAssets(result.data.portfolioAssets);

      // Обновление активов кошельков
      if (result.data.walletAssets) updateWalletAssets(result.data.walletAssets);
    }
    
    setLoading(false);
    return result;
  };

  const deleteTransaction = async (transaction) => {
    // Валидация бизнес-правилами
    const validation = transactionService.validateDelete(transaction);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);

    // Вызов API
    const result = await transactionApi.deleteTransaction(transaction.id);

    // Редактирование
    if (result.success) {

      // Обновление активов портфелей
      if (result.data.portfolioAssets) updatePortfolioAssets(result.data.portfolioAssets);

      // Обновление активов кошельков
      if (result.data.walletAssets) updateWalletAssets(result.data.walletAssets);
    }
    
    setLoading(false);
    return result;
  };
  
  return { 
    editTransaction,
    deleteTransaction,
    loading
  };
};
