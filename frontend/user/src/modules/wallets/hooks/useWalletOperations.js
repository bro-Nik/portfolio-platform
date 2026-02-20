import { useState } from 'react';
import { walletService } from '../services/walletService'
import { useNavigation } from '/app/src/hooks/useNavigation';
import { useDataStore } from '/app/src/stores/dataStore';
import { walletApi } from '../api/walletApi';

export const useWalletOperations = () => {
  const [loading, setLoading] = useState(false);

  const addWalletToStore = useDataStore(state => state.addWallet);
  const updateWalletInStore = useDataStore(state => state.updateWallet);
  const deleteWalletFromStore = useDataStore(state => state.deleteWallet);
  const { closeItem } = useNavigation();

  const editWallet = async (wallet) => {
    // Валидация бизнес-правилами
    const validation = walletService.validateEdit(wallet);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);

    // Вызов API
    const result = await walletApi.saveWallet(wallet);

    // Редактирование
    if (result.success && wallet.id) {
      updateWalletInStore(wallet.id, result.data);
    }
    
    // Создание
    if (result.success && !wallet.id) {
      addWalletToStore(result.data);
    }
    
    setLoading(false);
    return result;
  };
  
  const deleteWallet = async (wallet) => {
    // Валидация бизнес-правилами
    const validation = walletService.validateDelete(wallet);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);

    // Вызов API
    const result = await walletApi.deleteWallet(wallet.id);
    
    if (result.success) {
      deleteWalletFromStore(wallet.id);
      // Обновление состояния навигации
      closeItem(wallet.id, 'wallet')
    }
    
    setLoading(false);
    return result;
  };
  
  return { editWallet, deleteWallet, loading };
};
