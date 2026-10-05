import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios';
import { clearTokens } from './token.js';

type TokenProvider = (() => Promise<string | undefined>) | null;

const errorTranslations: Record<string, string> = {
  'Field required': 'обязательное поле',
  'Input should be a valid integer': 'должно быть числом',
  'Input should be a valid string': 'должно быть строкой',
  'ensure this value is not empty': 'не должно быть пустым',
};

const translateError = (msg: string): string => errorTranslations[msg] || msg;

const parseErrorMessage = (data: Record<string, unknown> | null): string => {
  if (!data) return 'Ошибка запроса';

  if (data.detail) {
    if (Array.isArray(data.detail)) {
      return (data.detail as Array<Record<string, unknown>>)
        .map((d) => {
          const loc = d.loc as string[] | undefined;
          const field = loc?.[1] || loc?.[0] || 'поле';
          const msg = translateError(d.msg as string);
          return `${field}: ${msg}`;
        })
        .join(', ');
    }
    return data.detail as string;
  }

  if (data.message) return data.message as string;
  return 'Ошибка запроса';
};

export const apiService = (
  baseUrl = '',
  getToken?: TokenProvider,
  refreshProvider?: () => Promise<string | undefined>,
  sessionExpiredRedirect = '/login',
) => {
  const client: AxiosInstance = axios.create({
    baseURL: baseUrl,
    headers: { 'Content-Type': 'application/json' },
    // Массивы как повторяющийся ключ (markets=crypto), а не markets[]=crypto:
    // дефолт axios не понимает FastAPI Query() под list[str], и фильтр молча не работал.
    paramsSerializer: { indexes: null },
  });

  client.interceptors.request.use(async (config) => {
    if (getToken) {
      const token = await getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  });

  let refreshPromise: Promise<string | undefined> | null = null;

  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (error.response?.status === 401 && refreshProvider && !error.config._retry) {
        const originalRequest = error.config;
        originalRequest._retry = true;

        if (!refreshPromise) {
          refreshPromise = refreshProvider()
            .catch(() => undefined as string | undefined)
            .finally(() => {
              refreshPromise = null;
            });
        }

        const newToken = await refreshPromise;
        if (newToken) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return client(originalRequest);
        }

        clearTokens();
        window.location.href = sessionExpiredRedirect;
        throw new Error('Сессия истекла');
      }

      if (error.response) {
        const data = error.response.data as Record<string, unknown> | null;
        const message = parseErrorMessage(data);
        console.error('Ошибка запроса:', baseUrl + error.config?.url, message);
        throw new Error(message);
      }
      console.error('Ошибка сети:', baseUrl + error.config?.url);
      throw new Error('Ошибка сети');
    },
  );

  const get = <T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    client.get(url, config).then((r) => r.data as T);

  const post = <T = unknown>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    return client.post(url, body, config).then((r) => r.data as T);
  };

  const put = <T = unknown>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    return client.put(url, body, config).then((r) => r.data as T);
  };

  const patch = <T = unknown>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    return client.patch(url, body, config).then((r) => r.data as T);
  };

  const del = <T = unknown>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    const mergedConfig: AxiosRequestConfig = { ...config, data: body ?? config?.data };
    return client.delete(url, mergedConfig).then((r) => r.data as T);
  };

  return { get, post, put, patch, del };
};

export type ApiService = ReturnType<typeof apiService>;
