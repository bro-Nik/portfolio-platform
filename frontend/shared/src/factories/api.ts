import { apiService } from '../services/api.js';
import { authService } from '../services/auth.js';

interface CreateApiOptions {
  useAuth?: boolean;
  sessionExpiredRedirect?: string;
}

export const createApi = (baseUrl?: string, options: CreateApiOptions = {}) => {
  const { useAuth = false, sessionExpiredRedirect = '/login' } = options;

  const tokenProvider = useAuth ? () => authService().getValidToken() : null;
  const refreshProvider = useAuth
    ? async () => {
        try {
          return await authService().refreshTokens();
        } catch {
          return undefined;
        }
      }
    : undefined;

  return apiService(baseUrl, tokenProvider, refreshProvider, sessionExpiredRedirect);
};
