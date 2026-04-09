import { getToken, getRefreshToken, setTokens, decodeToken, isTokenExpired, clearTokens } from './token.js';
import { apiService } from './api.js';

export const authService = () => {
  const api = apiService(process.env.REACT_APP_AUTH_SERVICE_URL);

  const getCurrentUser = async () => {
    const token = await getValidToken();
    let decodedToken = decodeToken(token);
    if (!decodedToken) return;

    return {
      id: decodedToken.id,
      login: decodedToken.login,
      role: decodedToken.role,
    }
  };

  const getValidToken = async () => {
    let token = getToken();
    let decodedToken = decodeToken(token);
    if (!decodedToken) return;

    if (!isTokenExpired(decodedToken)) return token;

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

  const setTokensFromResponse = (data) => {
    const { accessToken, refreshToken } = data;
    if (!accessToken && !refreshToken) throw new Error('Не получены токены авторизации');
    if (!accessToken) throw new Error('Нет access токена');
    if (!refreshToken) throw new Error('Нет refresh токена');

    setTokens(accessToken, refreshToken);
  };

  const login = async (email, password) => {
    try {
      const data = await api.post('/login', { email, password });
      setTokensFromResponse(data);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error?.message || 'Ошибка входа' };
    }
  };

  const register = async (email, password) => {
    try {
      const data = await api.post('/register', { email, password });
      setTokensFromResponse(data);
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error?.message || 'Ошибка регистрации' };
    }
  };

  const refreshTokens = async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) throw new Error('Нет refresh токена');

    const data = await api.post('/refresh', { token: refreshToken });
    setTokensFromResponse(data);
    return data.accessToken;
  };

  const logout = async () => {
    const accessToken = getToken();
    const refreshToken = getRefreshToken();
    clearTokens();

    if (refreshToken) {
      api.post('/logout', { token: refreshToken }, accessToken).catch(() => {});
    }
  };

  return {
    login,
    register,
    logout,
    getCurrentUser,
    getValidToken
  };
};
