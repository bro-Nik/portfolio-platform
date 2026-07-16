import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider, theme } from 'antd';
import './index.css';
import App from './App';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useThemeStore } from '@portfolio/shared';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
  },
});

const darkTheme = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    colorBgLayout: '#1a1f2e',
    colorBgContainer: '#242a3d',
    colorBgElevated: '#2d3448',
  },
};

const lightThemeConfig = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
  },
};

const ThemedApp = () => {
  const { theme: currentTheme } = useThemeStore();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', currentTheme);
  }, [currentTheme]);

  return (
    <ConfigProvider
      theme={currentTheme === 'dark' ? darkTheme : lightThemeConfig}
    >
      <App />
    </ConfigProvider>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemedApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>
);
