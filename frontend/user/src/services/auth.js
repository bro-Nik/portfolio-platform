import { apiService } from './api';
import { getToken, getRefreshToken, setTokens, decodeToken, isTokenExpired } from './token';

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

    // Если токен просрочен, пытаемся обновить
    if (isTokenExpired(decodedToken)) {
      console.log('Токен просрочен, пытаемся обновить...');
      token = await refreshTokens();
      decodedToken = decodeToken(token);
      if (!decodedToken) return;
      console.log('Токен обновлен');
    }
    return token;
  };

  const setTokensFromResponse = (data) => {
    const { accessToken, refreshToken } = data;
    setTokens(accessToken, refreshToken);
  };

  const login = async (email, password) => {
    const result = await api.post('/login', { email, password });
    if (result.success) setTokensFromResponse(result.data);
    return result;
  };

  const register = async (email, password) => {
    const result = await api.post('/register', { email, password });
    if (result.success) setTokensFromResponse(result.data);
    return result;
  };

  const refreshTokens = async () => {
    const token = getRefreshToken();
    if (!token) throw new Error('No refresh token');

    const result = await api.post('/refresh', { token });
    if (result.success) {
      setTokensFromResponse(result.data);
      return result.data.accessToken;
    }
  };

  const logout = async () => {
    const token = getRefreshToken();
    if (!token) throw new Error('No refresh token');

    return await api.post('/logout', { token });
  };

  return {
    login,
    register,
    refreshTokens,
    logout,
    getCurrentUser,
    getValidToken
  };
};
