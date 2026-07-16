import { apiService } from '../services/api.js';
import { authService } from '../services/auth.js';

interface CreateApiOptions {
  useAuth?: boolean;
  convertCase?: boolean;
}

export const createApi = (baseUrl?: string, options: CreateApiOptions = {}) => {
  const { useAuth = false, convertCase = false } = options;

  const tokenProvider = useAuth ? () => authService().getValidToken() : null;

  return apiService(baseUrl, tokenProvider, convertCase);
};
