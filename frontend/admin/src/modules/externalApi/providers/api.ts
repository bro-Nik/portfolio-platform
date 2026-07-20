import { createApi } from '@portfolio/shared';
import { CreateProviderData, Provider, ProviderLog, ProviderPreset, ProviderStats, ProviderWithMethods, UpdateProviderData } from '../../../types/provider';

const baseUrl = `${process.env.REACT_APP_MARKET_SERVICE_URL}/admin/providers`;
const api = createApi(baseUrl, { useAuth: true });

export const providersApi = {
  getProviders: (): Promise<Provider[]> => {
    return api.get('');
  },

  createProvider: (data: CreateProviderData): Promise<Provider> => {
    return api.post('', data);
  },

  updateProvider: (name: string, data: UpdateProviderData): Promise<Provider> => {
    return api.put(`/${encodeURIComponent(name)}`, data);
  },

  deleteProvider: (name: string): Promise<void> => {
    return api.del(`/${encodeURIComponent(name)}`);
  },

  resetCountersProvider: (name: string): Promise<void> => {
    return api.post(`/${encodeURIComponent(name)}/reset-counters`);
  },

  getProviderLogs: (name: string): Promise<ProviderLog[]> => {
    return api.get(`/${encodeURIComponent(name)}/logs?hours=24&limit=20`);
  },

  getProviderStats: (name: string): Promise<ProviderStats> => {
    return api.get(`/${encodeURIComponent(name)}/stats`);
  },

  getProvidersWithPresets: (): Promise<ProviderPreset[]> => {
    return api.get('/with/settings');
  },

  getProvidersWithMethods: (): Promise<ProviderWithMethods[]> => {
    return api.get('/with/methods');
  },
};
