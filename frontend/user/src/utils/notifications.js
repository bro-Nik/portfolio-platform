import { notification } from 'antd';

const DEFAULT_PLACEMENT = 'topRight';

export const destroyNotifications = () => {
  notification.destroy();
};

export const successToast = (description) => {
  notification.success({
    message: 'Успешно',
    description,
    placement: DEFAULT_PLACEMENT,
    duration: 3,
  });
};

export const errorToast = (error, fallback = 'Произошла ошибка') => {
  const message = error?.response?.data?.detail || error?.message || error || fallback;
  notification.error({
    message: 'Ошибка',
    description: message,
    placement: DEFAULT_PLACEMENT,
    duration: 5,
  });
};

export const persistentErrorToast = (error) => {
  const message = error?.response?.data?.detail || error?.message || error || 'Произошла ошибка';
  notification.error({
    message: 'Ошибка',
    description: message,
    placement: DEFAULT_PLACEMENT,
    duration: 0,
  });
};

export const warningToast = (description) => {
  notification.warning({
    message: 'Внимание',
    description,
    placement: DEFAULT_PLACEMENT,
    duration: 5,
  });
};
