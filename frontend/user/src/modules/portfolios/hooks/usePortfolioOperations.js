import { useState } from 'react';
import { portfolioService } from '../services/portfolioService'
import { useNavigation } from 'src/hooks/useNavigation';
import { usePortfolioMutations } from './usePortfolioMutations';

export const usePortfolioOperations = () => {
  const [loading, setLoading] = useState(false);

  const { closeItem } = useNavigation();
  const mutations = usePortfolioMutations();

  const editPortfolio = async (portfolio) => {
    const validation = portfolioService.validateEdit(portfolio);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }

    setLoading(true);
    try {
      const data = await mutations.editPortfolio.mutateAsync(portfolio);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const deletePortfolio = async (portfolio) => {
    const validation = portfolioService.validateDelete(portfolio);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }

    setLoading(true);
    try {
      await mutations.deletePortfolio.mutateAsync(portfolio);
      closeItem(portfolio.id, 'portfolio');
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const addAsset = async (portfolio, asset) => {
    const validation = portfolioService.validateAddAsset(portfolio, asset);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }

    setLoading(true);
    try {
      const data = await mutations.addAsset.mutateAsync({ portfolio, asset });
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const deleteAsset = async (portfolio, asset) => {
    const validation = portfolioService.validateDeleteAsset(portfolio, asset);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }

    setLoading(true);
    try {
      const data = await mutations.deleteAsset.mutateAsync({ portfolio, asset });
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  return {
    editPortfolio,
    deletePortfolio,
    addAsset,
    deleteAsset,
    loading
  };
};
