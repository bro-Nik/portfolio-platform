import { notification } from 'antd';
import { getErrorMessage } from './errorUtils';

export const errorNotification = (error: Error, title: string = 'Ошибка'): void => {
  notification.error({
    title: title,
    description: getErrorMessage(error),
    duration: 5,
  });
  console.error('API Error:', error);
};

export const successNotification = (description: string): void => {
  notification.success({
    title: 'Успешно',
    description: description,
    duration: 3,
  });
};
