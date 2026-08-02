import { createApi } from '@portfolio/shared';

const api = createApi(import.meta.env.VITE_AUTH_SERVICE_URL, { useAuth: true });

export const settingsApi = {
  getProfile: () => api.get('/me'),
};
