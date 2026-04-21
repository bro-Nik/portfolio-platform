import { apiService } from '../services/api.js';
import { authService } from '../services/auth.js';

export const createApi = (baseUrl, options = {}) => {
  const { getValidToken } = authService();
  const { useAuth = false, convertCase = false } = options;

  const tokenProvider = useAuth ? getValidToken : null;

  return apiService(baseUrl, tokenProvider, convertCase);
};
