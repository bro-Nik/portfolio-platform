import { createApi } from '@portfolio/shared';
import { API_BASE } from 'src/constants/api';

const api = createApi(API_BASE.transactions, { useAuth: true });

export const transactionApi = {
  saveTransaction: (transactionData) => {
    if (transactionData.id) {
      return api.put(`/${transactionData.id}`, transactionData);
    } else {
      return api.post('', transactionData);
    }
  },
  deleteTransaction: (transactionId) => api.del(`/${transactionId}`),
};
