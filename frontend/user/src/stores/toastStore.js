import { create } from 'zustand';

export const useToastStore = create((set, get) => ({
  toasts: [],

  // Добавление тоста
  addToast: (message, type = 'info') => {
    const id = Date.now() + Math.random();
    const toast = { id, message, type };

    set((state) => ({
      toasts: [...state.toasts, toast],
    }));

    // Автоматическое удаление для не-ошибок
    if (type !== 'error') {
      setTimeout(() => {
        get().removeToast(id);
      }, 5000);
    }

    return id;
  },

  // Удаление тоста по ID
  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    }));
  },

  // Очистка всех тостов
  clearToasts: () => {
    set({ toasts: [] });
  },

  // Вспомогательные методы для разных типов тостов
  success: (message) => get().addToast(message, 'success'),
  error: (message) => get().addToast(message, 'error'),
  warning: (message) => get().addToast(message, 'warning'),
  info: (message) => get().addToast(message, 'info'),
}));
