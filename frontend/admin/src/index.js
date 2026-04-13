import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider, theme } from 'antd';
import './index.css';
import App from './App';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Создаем клиент React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,                    // Повторить 1 раз при ошибке
      staleTime: 5 * 60 * 1000,    // 5 минут данные считаются свежими
      refetchOnWindowFocus: true,  // Обновлять при фокусе окна
      refetchOnReconnect: true,    // Обновлять при восстановлении сети
    },
  },
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        theme={{
          algorithm: theme.defaultAlgorithm,
          token: {
            colorPrimary: '#1890ff',
            borderRadius: 6,
          },
        }}
      >
        <App />
      </ConfigProvider>

      {/* DevTools - только для разработки */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>
);
