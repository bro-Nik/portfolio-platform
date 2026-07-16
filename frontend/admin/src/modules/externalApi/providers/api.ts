import { createApi } from '@portfolio/shared';
import { CreateProviderData, Provider, ProviderLog, ProviderPreset, ProviderStats, ProviderWithMethods, UpdateProviderData } from '../../../types/provider';

const baseUrl = `${process.env.REACT_APP_MARKET_SERVICE_URL}/admin/providers`;
const api = createApi(baseUrl, { convertCase: true, useAuth: true });

export const providersApi = {
  getProviders: (): Promise<Provider[]> => {
    return api.get('');
  },

  createProvider: (data: CreateProviderData): Promise<Provider> => {
    return api.post('', data);
  },

  updateProvider: (id: number, data: UpdateProviderData): Promise<Provider> => {
    return api.put(`/${id}`, data);
  },

  deleteProvider: (id: number): Promise<void> => {
    return api.del(`/${id}`);
  },

  resetCountersProvider: (id: number): Promise<void> => {
    return api.post(`/${id}/reset-counters`);
  },

  getProviderLogs: (id: number): Promise<ProviderLog[]> => {
    return api.get(`/${id}/logs?hours=24&limit=20`);
  },

  getProviderStats: (id: number): Promise<ProviderStats> => {
    return api.get(`/${id}/stats`);
  },

  getProvidersWithPresets: (): Promise<ProviderPreset[]> => {
    return api.get('/with/settings');
  },

  getProvidersWithMethods: (): Promise<ProviderWithMethods[]> => {
    return api.get('/with/methods');
  },
};
