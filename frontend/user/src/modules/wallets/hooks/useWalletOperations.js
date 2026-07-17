import { useState } from 'react';
import { walletService } from '../services/walletService'
import { useNavigation } from 'src/hooks/useNavigation';
import { useWalletMutations } from './useWalletMutations';

export const useWalletOperations = () => {
  const [loading, setLoading] = useState(false);

  const { closeItem } = useNavigation();
  const mutations = useWalletMutations();

  const editWallet = async (wallet) => {
    const validation = walletService.validateEdit(wallet);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }

    setLoading(true);
    try {
      const data = await mutations.editWallet.mutateAsync(wallet);
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
      await mutations.deleteWallet.mutateAsync(wallet);
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
