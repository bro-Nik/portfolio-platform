import { authService } from './auth.js';
import { apiService } from './api.js';

export const createApi = (baseUrl, options = {}) => {
  const { getValidToken } = authService();
  const { convertCase = true, useAuth = false } = options;
  
  const tokenProvider = useAuth ? getValidToken : null;
  
  return apiService(baseUrl, tokenProvider, { convertCase });
};
