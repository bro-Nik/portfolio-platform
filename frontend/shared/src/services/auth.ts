import { getToken, setTokens, decodeToken, isTokenExpired, clearTokens, getStoredLogin, setStoredLogin } from './token.js';
import { apiService } from './api.js';
import { createApi } from '../factories/api.js';

const AUTH_SERVICE_URL = import.meta.env.VITE_AUTH_SERVICE_URL;

export const authService = () => {
  const computeLogin = (email: string): string => email.split('@')[0] ?? '';

  const setAccessTokenFromResponse = (data: { accessToken?: string }) => {
    if (!data.accessToken) throw new Error('Не получен access токен');
    setTokens(data.accessToken);
  };

  const refreshTokens = async (): Promise<string> => {
    const data = await api.post('/refresh') as { accessToken: string };
    setAccessTokenFromResponse(data);
    return data.accessToken;
  };

  const getValidToken = async (): Promise<string | undefined> => {
    let token = getToken();
    const decodedToken = decodeToken(token);
    if (!decodedToken) return;

    if (!isTokenExpired(decodedToken)) return token ?? undefined;

    try {
      token = await refreshTokens();
      if (!token) return;
      return token;
    } catch {
      clearTokens();
    }
  };

  const api = apiService(AUTH_SERVICE_URL);
  const authApi = createApi(AUTH_SERVICE_URL, { useAuth: true });

  const getCurrentUser = async (): Promise<{ id: string; login: string; role: string } | undefined> => {
    const token = await getValidToken();
    const decodedToken = decodeToken(token ?? null);
    if (!decodedToken) return;

    return {
      id: decodedToken.id,
      login: getStoredLogin(),
      role: decodedToken.role ?? '',
    };
  };

  const login = async (email: string, password: string): Promise<{ success: boolean; data?: unknown; error?: string }> => {
    try {
      const data = await api.post('/login', { email, password });
      setAccessTokenFromResponse(data as { accessToken?: string });
      setStoredLogin(computeLogin(email));
      return { success: true, data };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка входа' };
    }
  };

  const register = async (email: string, password: string): Promise<{ success: boolean; data?: unknown; error?: string }> => {
    try {
      const data = await api.post('/register', { email, password });
      setAccessTokenFromResponse(data as { accessToken?: string });
      setStoredLogin(computeLogin(email));
      return { success: true, data };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка регистрации' };
    }
  };

  const logout = async (): Promise<void> => {
    clearTokens();
    api.post('/logout').catch(() => {});
  };

  const verifyEmail = async (token: string): Promise<{ success: boolean; data?: unknown; error?: string }> => {
    try {
      const data = await api.post('/verify-email', { token });
      try {
        await refreshTokens();
      } catch {
        // пользователь может быть не залогинен — не страшно
      }
      return { success: true, data };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка подтверждения email' };
    }
  };

  const resendVerification = async (): Promise<{ success: boolean; message?: string; error?: string }> => {
    try {
      const data = await authApi.post('/resend-verification', {}) as { message?: string };
      return { success: true, message: data?.message };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка отправки письма' };
    }
  };

  const changePassword = async (currentPassword: string, newPassword: string): Promise<{ success: boolean; error?: string }> => {
    try {
      await authApi.put('/password', { currentPassword, newPassword });
      return { success: true };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка смены пароля' };
    }
  };

  const getSessions = async (): Promise<{ success: boolean; data?: unknown[]; error?: string }> => {
    try {
      const data = await authApi.get('/sessions');
      return { success: true, data: data as unknown[] };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка получения сессий' };
    }
  };

  const deleteSession = async (sessionId: number): Promise<{ success: boolean; error?: string }> => {
    try {
      await authApi.del(`/sessions/${sessionId}`);
      return { success: true };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка удаления сессии' };
    }
  };

  const logoutAll = async (): Promise<{ success: boolean; error?: string }> => {
    try {
      await authApi.post('/logout-all');
      return { success: true };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка выхода со всех устройств' };
    }
  };

  const forgotPassword = async (email: string): Promise<{ success: boolean; message?: string; error?: string }> => {
    try {
      const data = await api.post('/forgot-password', { email }) as { message?: string };
      return { success: true, message: data?.message };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка восстановления пароля' };
    }
  };

  const resetPassword = async (token: string, password: string): Promise<{ success: boolean; message?: string; error?: string }> => {
    try {
      const data = await api.post('/reset-password', { token, password }) as { message?: string };
      return { success: true, message: data?.message };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка сброса пароля' };
    }
  };

  const changeEmail = async (currentPassword: string, newEmail: string): Promise<{ success: boolean; message?: string; error?: string }> => {
    try {
      const data = await authApi.put('/email', { currentPassword, newEmail }) as { message?: string };
      setStoredLogin(computeLogin(newEmail));
      return { success: true, message: data?.message };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка смены email' };
    }
  };

  const deleteAccount = async (currentPassword: string): Promise<{ success: boolean; error?: string }> => {
    try {
      await authApi.del('/account', { currentPassword });
      return { success: true };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка удаления аккаунта' };
    }
  };

  return {
    login,
    register,
    logout,
    verifyEmail,
    resendVerification,
    forgotPassword,
    resetPassword,
    changePassword,
    changeEmail,
    getSessions,
    deleteSession,
    logoutAll,
    deleteAccount,
    getCurrentUser,
    getValidToken,
    refreshTokens,
  };
};

export type AuthService = ReturnType<typeof authService>;
