export const portfolioService = {
  validateEdit() {
    return { isValid: true };
  },

  validateDelete() {
    // ToDo Дополнительные проверки:
    // - есть ли право у пользователя

    return { isValid: true };
  },

  validateAddAsset(portfolio, asset) {
    if (!portfolio?.id) {
      return { isValid: false, error: 'Портфель не указан' };
    }
    
    if (!asset?.id) {
      return { isValid: false, error: 'Актив не указан' };
    }

    const isDuplicate = portfolio.assets?.some(a => a.tickerId === asset.id);
    if (isDuplicate) {
      return { isValid: false, error: 'Этот актив уже добавлен в портфель' };
    }

    return { isValid: true };
  },

  validateDeleteAsset(portfolio, asset) {
    if (!portfolio?.id) {
      return { isValid: false, error: 'Портфель не указан' };
    }
    
    if (!asset?.id) {
      return { isValid: false, error: 'Актив не указан' };
    }

    return { isValid: true };
  },
  
};
