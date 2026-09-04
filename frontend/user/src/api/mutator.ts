import type { AxiosRequestConfig } from 'axios';
import { createApi } from '@portfolio/shared';

const api = createApi('', { useAuth: true });

export const mutator = <T>(config: AxiosRequestConfig): Promise<T> => {
  const { method = 'get', url, data, params, headers } = config;
  const requestConfig = { params, headers };

  switch (method) {
    case 'post':
      return api.post<T>(url!, data, requestConfig);
    case 'put':
      return api.put<T>(url!, data, requestConfig);
    case 'patch':
      return api.patch<T>(url!, data, requestConfig);
    case 'delete':
      return data !== undefined
        ? api.del<T>(url!, { ...requestConfig, data })
        : api.del<T>(url!, requestConfig);
    default:
      return api.get<T>(url!, requestConfig);
  }
};
