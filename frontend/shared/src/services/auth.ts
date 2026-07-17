import { getToken, getRefreshToken, setTokens, decodeToken, isTokenExpired, clearTokens } from './token.js';
import { apiService } from './api.js';
import { createApi } from '../factories/api.js';

declare const process: {
  env: {
    REACT_APP_AUTH_SERVICE_URL?: string;
  };
};

export const authService = () => {
  const setTokensFromResponse = (data: { accessToken?: string; refreshToken?: string }) => {
    const { accessToken, refreshToken } = data;
    if (!accessToken && !refreshToken) throw new Error('Не получены токены авторизации');
    if (!accessToken) throw new Error('Нет access токена');
    if (!refreshToken) throw new Error('Нет refresh токена');

    setTokens(accessToken, refreshToken);
  };

  const refreshTokens = async (): Promise<string> => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) throw new Error('Нет refresh токена');

    const data = await api.post('/refresh', { token: refreshToken }) as { accessToken: string };
    setTokensFromResponse(data);
    return data.accessToken;
  };

  const getValidToken = async (): Promise<string | undefined> => {
    let token = getToken();
    let decodedToken = decodeToken(token);
    if (!decodedToken) return;

    if (!isTokenExpired(decodedToken)) return token ?? undefined;

    try {
      token = await refreshTokens();
      if (!token) return;
      console.log('Токены авторизации обновлены');
      return token;
    } catch (error) {
      console.error('Ошибка обновления токенов авторизации:', error);
      clearTokens();
    }
  };

  const api = apiService(process.env.REACT_APP_AUTH_SERVICE_URL);
  const authApi = createApi(process.env.REACT_APP_AUTH_SERVICE_URL, { useAuth: true });

  const getCurrentUser = async (): Promise<{ id: string; login: string; role: string; email: string; isVerified: boolean } | undefined> => {
    const token = await getValidToken();
    const decodedToken = decodeToken(token ?? null);
    if (!decodedToken) return;

    return {
      id: decodedToken.id,
      login: decodedToken.login ?? '',
      role: decodedToken.role ?? '',
      email: decodedToken.email ?? '',
      isVerified: decodedToken.is_verified ?? false,
    };
  };

  const login = async (email: string, password: string): Promise<{ success: boolean; data?: unknown; error?: string }> => {
    try {
      const data = await api.post('/login', { email, password });
      setTokensFromResponse(data as { accessToken?: string; refreshToken?: string });
      return { success: true, data };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка входа' };
    }
  };

  const register = async (email: string, password: string): Promise<{ success: boolean; data?: unknown; error?: string }> => {
    try {
      const data = await api.post('/register', { email, password });
      setTokensFromResponse(data as { accessToken?: string; refreshToken?: string });
      return { success: true, data };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка регистрации' };
    }
  };

  const logout = async (): Promise<void> => {
    const refreshToken = getRefreshToken();
    clearTokens();

    if (refreshToken) {
      api.post('/logout', { token: refreshToken }).catch(() => {});
    }
  };

  const verifyEmail = async (token: string): Promise<{ success: boolean; data?: unknown; error?: string }> => {
    try {
      const data = await api.post('/verify-email', { token });
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

  const changeEmail = async (currentPassword: string, newEmail: string): Promise<{ success: boolean; error?: string }> => {
    try {
      await authApi.put('/email', { currentPassword, newEmail });
      return { success: true };
    } catch (error) {
      return { success: false, error: (error as Error)?.message || 'Ошибка смены email' };
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
    getCurrentUser,
    getValidToken,
  };
};

export type AuthService = ReturnType<typeof authService>;
