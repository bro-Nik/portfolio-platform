import { createApi } from '@portfolio/shared';

const api = createApi(process.env.REACT_APP_AUTH_SERVICE_URL, { useAuth: true });

export const settingsApi = {
  getProfile: () => api.get('/me'),
};
