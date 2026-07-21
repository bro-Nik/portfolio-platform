import { App } from 'antd';

export const useNotifications = () => {
  const { notification } = App.useApp();

  const success = (description: string) => {
    notification.success({ description, duration: 3, placement: 'topRight' });
  };

  const error = (description: string) => {
    notification.error({ description, duration: 5, placement: 'topRight' });
  };

  const persistentError = (description: string) => {
    notification.error({ description, duration: 0, placement: 'topRight' });
  };

  const warning = (description: string) => {
    notification.warning({ description, duration: 5, placement: 'topRight' });
  };

  const destroy = () => {
    notification.destroy();
  };

  return { success, error, persistentError, warning, destroy };
};
