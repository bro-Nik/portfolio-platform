export const transactionService = {
  validateEdit(transaction) {
    return { isValid: true };
  },

  validateDelete(transaction) {
    // ToDo Дополнительные проверки:
    // - есть ли право у пользователя

    return { isValid: true };
  },
  
};
