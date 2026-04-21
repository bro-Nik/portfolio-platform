import { notification } from 'antd';

export const errorNotification = (error: unknown, title: string = 'Ошибка'): void => {
  const message = error instanceof Error ? error.message : String(error);
  notification.error({
    title: title,
    description: message,
    duration: 5,
  });
};

export const successNotification = (description: string): void => {
  notification.success({
    title: 'Успешно',
    description: description,
    duration: 3,
  });
};
