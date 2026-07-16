import { createApi } from '@portfolio/shared';

const api = createApi('/api/transactions', { useAuth: true, convertCase: true });

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
