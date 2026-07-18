import { apiService } from '../services/api.js';
import { authService } from '../services/auth.js';

interface CreateApiOptions {
  useAuth?: boolean;
}

export const createApi = (baseUrl?: string, options: CreateApiOptions = {}) => {
  const { useAuth = false } = options;

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

  return apiService(baseUrl, tokenProvider, refreshProvider);
};
