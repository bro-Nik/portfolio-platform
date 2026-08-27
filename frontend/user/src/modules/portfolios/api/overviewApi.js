import { createApi } from '@portfolio/shared';
import { API_BASE } from 'src/constants/api';

const api = createApi(API_BASE.overview, { useAuth: true });

export const fetchOverview = () => api.get('');
