import { jwtDecode } from 'jwt-decode';

interface TokenPayload {
  id: string;
  login?: string;
  role?: string;
  email?: string;
  is_verified?: boolean;
  exp: number;
  [key: string]: unknown;
}

export function getToken(): string | null {
  return localStorage.getItem('accessToken');
}

export function getRefreshToken(): string | null {
  return localStorage.getItem('refreshToken');
}

export function setTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem('accessToken', accessToken);
  localStorage.setItem('refreshToken', refreshToken);
}

export function clearTokens(): void {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
}

export const decodeToken = (token: string | null): TokenPayload | null => {
  try {
    return jwtDecode<TokenPayload>(token || '');
  } catch {
    return null;
  }
};

export const isTokenExpired = (decoded: { exp: number } | null): boolean => {
  if (!decoded || !decoded.exp) return true;

  const threshold = 5;
  const currentTime = Date.now() / 1000;
  return decoded.exp - currentTime < threshold;
};

export function isTokenValid(token: string): boolean {
  if (!token) return false;

  const parts = token.split('.');

  if (parts.length !== 3) return false;

  try {
    const payload = JSON.parse(atob(parts[1]));

    if (Date.now() >= payload.exp * 1000) return false;
    if (!payload.id || !payload.exp) return false;

    return true;
  } catch {
    return false;
  }
}
