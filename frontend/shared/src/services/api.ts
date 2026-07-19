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

const snakeToCamel = (obj: unknown): unknown => {
  if (obj === undefined || obj === null) return obj;

  if (Array.isArray(obj)) {
    return obj.map(v => snakeToCamel(v));
  } else if (obj !== null && typeof obj === 'object' && obj.constructor === Object) {
    return Object.keys(obj as Record<string, unknown>).reduce((result, key) => {
      const camelKey = key.replace(/_([a-z])/g, (_, letter: string) => letter.toUpperCase());
      (result as Record<string, unknown>)[camelKey] = snakeToCamel((obj as Record<string, unknown>)[key]);
      return result;
    }, {} as Record<string, unknown>);
  }
  return obj;
};

const camelToSnake = (obj: unknown): unknown => {
  if (obj === undefined || obj === null) return obj;

  if (Array.isArray(obj)) {
    return obj.map(v => camelToSnake(v));
  } else if (obj !== null && typeof obj === 'object' && obj.constructor === Object) {
    return Object.keys(obj as Record<string, unknown>).reduce((result, key) => {
      const snakeKey = key.replace(/([A-Z])/g, (_, letter: string) => `_${letter.toLowerCase()}`);
      (result as Record<string, unknown>)[snakeKey] = camelToSnake((obj as Record<string, unknown>)[key]);
      return result;
    }, {} as Record<string, unknown>);
  }
  return obj;
};

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

export const apiService = (baseUrl = '', getToken?: TokenProvider, refreshProvider?: () => Promise<string | undefined>) => {
  const client: AxiosInstance = axios.create({
    baseURL: baseUrl,
    headers: { 'Content-Type': 'application/json' },
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
    (response) => {
      response.data = snakeToCamel(response.data);
      return response;
    },
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
        window.location.href = '/login';
        throw new Error('Сессия истекла');
      }

      if (error.response) {
        const data = snakeToCamel(error.response.data) as Record<string, unknown> | null;
        const message = parseErrorMessage(data);
        console.error('Ошибка запроса:', baseUrl + error.config?.url, message);
        throw new Error(message);
      }
      console.error('Ошибка сети:', baseUrl + error.config?.url);
      throw new Error('Ошибка сети');
    },
  );

  const get = <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    client.get(url, config).then((r) => r.data as T);

  const post = <T = any>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    return client.post(url, camelToSnake(body), config).then((r) => r.data as T);
  };

  const put = <T = any>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    return client.put(url, camelToSnake(body), config).then((r) => r.data as T);
  };

  const del = <T = any>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    const mergedConfig: AxiosRequestConfig = { ...config, data: body ? camelToSnake(body) : config?.data };
    return client.delete(url, mergedConfig).then((r) => r.data as T);
  };

  return { get, post, put, del };
};

export type ApiService = ReturnType<typeof apiService>;
