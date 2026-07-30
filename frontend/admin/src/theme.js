import { theme } from 'antd';

const sharedComponents = {
  Alert: {
    lineWidth: 0,
  },
  Button: {
    colorBorderDisabled: 'transparent',
  },
};

export const darkTheme = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    colorBgLayout: '#1a1f2e',
    colorBgContainer: '#242a3d',
    colorBgElevated: '#2d3448',
  },
  components: sharedComponents,
};

export const lightTheme = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
  },
  components: sharedComponents,
};
