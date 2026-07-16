import { useState } from 'react';
import { walletService } from '../services/walletService'
import { useNavigation } from 'src/hooks/useNavigation';
import { useDataStore } from 'src/stores/dataStore';
import { walletApi } from '../api/walletApi';

export const useWalletOperations = () => {
  const [loading, setLoading] = useState(false);

  const addWalletToStore = useDataStore(state => state.addWallet);
  const updateWalletInStore = useDataStore(state => state.updateWallet);
  const deleteWalletFromStore = useDataStore(state => state.deleteWallet);
  const { closeItem } = useNavigation();

  const editWallet = async (wallet) => {
    const validation = walletService.validateEdit(wallet);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);
    try {
      const data = await walletApi.saveWallet(wallet);
      if (wallet.id) {
        updateWalletInStore(wallet.id, data);
      } else {
        addWalletToStore(data);
      }
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };
  
  const deleteWallet = async (wallet) => {
    const validation = walletService.validateDelete(wallet);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);
    try {
      await walletApi.deleteWallet(wallet.id);
      deleteWalletFromStore(wallet.id);
      closeItem(wallet.id, 'wallet');
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };
  
  return { editWallet, deleteWallet, loading };
};
