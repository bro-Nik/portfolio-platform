import { create } from 'zustand';
import { authService } from '../services/auth';
import { clearTokens } from '../services/token';

export const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  loading: true,
  isInitialized: false,

  // Действия
  initializeAuth: async () => {
    // Защита от повторной инициализации
    const { isInitialized } = get();
    if (isInitialized) return;

    set({
      loading: true,
      isInitialized: true,
    });
    
    try {
      const { getCurrentUser } = authService();
      const userData = await getCurrentUser();
      
      set({
        user: userData,
        isAuthenticated: !!userData,
        loading: false,
      });
    } catch (error) {
      set({
        user: null,
        isAuthenticated: false,
        loading: false,
      });
    }
  },

  login: async (userData) => {
    set({
      user: userData,
      isAuthenticated: !!userData,
    });
  },

  logout: () => {
    set({
      user: null,
      isAuthenticated: false,
    });
    clearTokens();
  },

  // Вспомогательные геттеры
  isAdmin: () => {
    const { user } = get();
    return user?.role === 'admin';
  },

  hasPermission: (permission) => {
    const { user } = get();
    return user?.permissions?.includes(permission);
  },
}));
