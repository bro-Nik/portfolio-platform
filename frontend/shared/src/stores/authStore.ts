import { create } from 'zustand';
import { authService } from '../services/auth.js';
import { clearTokens } from '../services/token.js';

interface User {
  id: string;
  login: string;
  role: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  isInitialized: boolean;
  initializeAuth: () => Promise<void>;
  login: (userData: User | null) => void;
  logout: () => void;
  isAdmin: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  loading: true,
  isInitialized: false,

  initializeAuth: async () => {
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
        user: userData ?? null,
        isAuthenticated: !!userData,
        loading: false,
      });
    } catch {
      set({
        user: null,
        isAuthenticated: false,
        loading: false,
      });
    }
  },

  login: (userData: User | null) => {
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

  isAdmin: () => {
    const { user } = get();
    return user?.role === 'admin';
  },
}));
