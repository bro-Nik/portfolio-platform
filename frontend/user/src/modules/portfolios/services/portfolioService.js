export const portfolioService = {
  validateEdit(portfolio) {
    return { isValid: true };
  },

  validateDelete(portfolio) {
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

    // ToDo Дополнительные проверки:
    // - есть ли право у пользователя
    // - не превышен лимит активов в портфеле
    // - не добавлен ли уже этот актив

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
