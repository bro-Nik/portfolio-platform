export const transactionService = {
  validateEdit() {
    return { isValid: true };
  },

  validateDelete() {
    // ToDo Дополнительные проверки:
    // - есть ли право у пользователя

    return { isValid: true };
  },
  
};
