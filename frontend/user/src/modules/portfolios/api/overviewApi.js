import { createApi } from '@portfolio/shared';

const api = createApi('/api/overview', { useAuth: true });

export const fetchOverview = () => api.get('');
