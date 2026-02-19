import { useState } from 'react';
import { portfolioService } from '../services/portfolioService'
import { useNavigation } from '/app/src/hooks/useNavigation';
import { portfolioApi } from '../api/portfolioApi';
import { useDataStore } from '/app/src/stores/dataStore';

export const usePortfolioOperations = () => {
  const [loading, setLoading] = useState(false);

  const { closeItem } = useNavigation();
  const addPortfolioToStore = useDataStore(state => state.addPortfolio);
  const updatePortfolioInStore = useDataStore(state => state.updatePortfolio);
  const deletePortfolioFromStore = useDataStore(state => state.deletePortfolio);

  const editPortfolio = async (portfolio) => {
    // Валидация бизнес-правилами
    const validation = portfolioService.validateEdit(portfolio);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);

    // Вызов API
    const result = await portfolioApi.savePortfolio(portfolio);

    if (result.success) {
      if (portfolio.id) {
        // Редактирование
        updatePortfolioInStore(result.data);
      } else {
        // Создание
        addPortfolioToStore(result.data);
      }
    }
    
    setLoading(false);
    return result;
  };
  
  const deletePortfolio = async (portfolio) => {
    // Валидация бизнес-правилами
    const validation = portfolioService.validateDelete(portfolio);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);

    // Вызов API
    const result = await portfolioApi.deletePortfolio(portfolio.id);
    
    if (result.success) {
      deletePortfolioFromStore(portfolio.id);
      // Обновление состояния навигации
      closeItem(portfolio.id, 'portfolio')
    }
    
    setLoading(false);
    return result;
  };

  const addAsset = async (portfolio, asset) => {
    // Валидация бизнес-правилами
    const validation = portfolioService.validateAddAsset(portfolio, asset);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);

    // Вызов API
    const result = await portfolioApi.addAssetToPortfolio(portfolio.id, asset.id);

    if (result.success) {
      updatePortfolioInStore(result.data);
    }
    
    setLoading(false);
    return result;
  }; 

  const deleteAsset = async (portfolio, asset) => {
    // Валидация бизнес-правилами
    const validation = portfolioService.validateDeleteAsset(portfolio, asset);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }
    
    setLoading(true);

    // Вызов API
    const result = await portfolioApi.delAssetFromPortfolio(portfolio.id, asset.id);
      
    if (result.success) {
      updatePortfolioInStore(result.data);
    }
      
    setLoading(false);
    return result;
  };
  
  return { 
    editPortfolio,
    deletePortfolio,
    addAsset,
    deleteAsset,
    loading
  };
};
