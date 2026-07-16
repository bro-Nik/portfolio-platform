import { useState } from 'react';
import { portfolioService } from '../services/portfolioService'
import { useNavigation } from 'src/hooks/useNavigation';
import { portfolioApi } from '../api/portfolioApi';
import { useDataStore } from 'src/stores/dataStore';

export const usePortfolioOperations = () => {
  const [loading, setLoading] = useState(false);

  const { closeItem } = useNavigation();
  const addPortfolioToStore = useDataStore(state => state.addPortfolio);
  const updatePortfolioInStore = useDataStore(state => state.updatePortfolio);
  const deletePortfolioFromStore = useDataStore(state => state.deletePortfolio);

  const editPortfolio = async (portfolio) => {
    const validation = portfolioService.validateEdit(portfolio);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);
    try {
      const data = await portfolioApi.savePortfolio(portfolio);
      if (portfolio.id) {
        updatePortfolioInStore(data);
      } else {
        addPortfolioToStore(data);
      }
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
      await portfolioApi.deletePortfolio(portfolio.id);
      deletePortfolioFromStore(portfolio.id);
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
      const data = await portfolioApi.addAssetToPortfolio(portfolio.id, asset.id);
      updatePortfolioInStore(data);
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
      const data = await portfolioApi.delAssetFromPortfolio(portfolio.id, asset.id);
      updatePortfolioInStore(data);
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
