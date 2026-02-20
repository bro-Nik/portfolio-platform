import { apiService } from '/app/src/services/api';
import { authService } from '/app/src/services/auth';

const { getValidToken } = authService();
const api = apiService('/api/transactions', getValidToken);

export const transactionApi = {
  saveTransaction: (transactionData) => {
    if (transactionData.id) {
      // Редактирование
      return api.put(`/${transactionData.id}`, transactionData, true);
    } else {
      // Создание
      return api.post('/', transactionData, true);
    }
  },
  deleteTransaction: (transactionId) => api.del(`/${transactionId}`),
};
