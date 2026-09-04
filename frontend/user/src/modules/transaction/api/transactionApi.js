import { getPortfolios } from 'src/api';

const portfolios = getPortfolios();

export const transactionApi = {
  saveTransaction: (transactionData) => {
    if (transactionData.id) {
      return portfolios.updateTransactionApiTransactionsTransactionIdPut(transactionData.id, transactionData);
    }
    return portfolios.createTransactionApiTransactionsPost(transactionData);
  },
  deleteTransaction: (transactionId) =>
    portfolios.deleteTransactionApiTransactionsTransactionIdDelete(transactionId),
};
