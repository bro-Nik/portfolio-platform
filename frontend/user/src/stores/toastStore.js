import { create } from 'zustand';
import { notification } from 'antd';

const typeMap = {
  success: 'success',
  warning: 'warning',
  info: 'info',
  error: 'error',
};

export const useToastStore = create(() => ({
  toasts: [],

  addToast: (message, type = 'info') => {
    const antType = typeMap[type] || 'info';
    notification[antType]({
      message,
      placement: 'topRight',
      duration: type === 'error' ? 0 : 5,
    });
  },

  removeToast: () => {},

  clearToasts: () => {
    notification.destroy();
  },

  success: (message) => notification.success({ message, placement: 'topRight', duration: 5 }),
  error: (message) => notification.error({ message, placement: 'topRight', duration: 0 }),
  warning: (message) => notification.warning({ message, placement: 'topRight', duration: 5 }),
  info: (message) => notification.info({ message, placement: 'topRight', duration: 5 }),
}));
