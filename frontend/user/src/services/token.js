import { jwtDecode } from 'jwt-decode';

export function getToken () {
  return localStorage.getItem('accessToken')
}

export function getRefreshToken () {
  return localStorage.getItem('refreshToken')
}

export function setTokens (accessToken, refreshToken) {
  localStorage.setItem('accessToken', accessToken);
  localStorage.setItem('refreshToken', refreshToken);
}

export function clearTokens () {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
}

export const decodeToken = (token) => {
  try {
    return jwtDecode(token);
  } catch (error) {
    return null;
  }
};

export const isTokenExpired = (decoded) => {
  if (!decoded || !decoded.exp) return true;
  
  // Погрешность (sec)
  const threshold = 5;

  const currentTime = Date.now() / 1000;
  return decoded.exp - currentTime < threshold;
};

export function isTokenValid (token) {
  if (!token) return false;

  const parts = token.split('.');

  // Проверка структуры токена
  if (parts.length !== 3) return false;

  try {
    const payload = JSON.parse(atob(parts[1]));
    
    // Проверка срока действия
    if (Date.now() >= payload.exp * 1000) return false;

    // Проверка необходимых полей
    if (!payload.sub || !payload.exp) return false;

    return true;
  } catch (error) {
    return false;
  }
}
