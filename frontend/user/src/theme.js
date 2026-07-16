import { theme } from 'antd';

const sharedTokens = {
  borderRadius: 8,
  fontSize: 14,
};

const sharedComponents = {
  Button: {
    borderRadius: 8,
    controlHeight: 36,
    borderRadiusLG: 10,
  },
  Card: {
    borderRadius: 12,
  },
  Modal: {
    borderRadius: 12,
  },
  Input: {
    borderRadius: 8,
  },
  InputNumber: {
    borderRadius: 8,
  },
  Select: {
    borderRadius: 8,
  },
  Menu: {
    borderRadius: 8,
  },
  Popover: {
    borderRadius: 10,
  },
  Tooltip: {
    borderRadius: 6,
  },
};

export const lightTheme = {
  token: {
    ...sharedTokens,
    colorPrimary: '#6366f1',
    colorBgLayout: '#f5f5f5',
    colorBgContainer: '#ffffff',
  },
  components: sharedComponents,
};

export const darkTheme = {
  algorithm: theme.darkAlgorithm,
  token: {
    ...sharedTokens,
    colorPrimary: '#6366f1',
    colorBgLayout: '#1a1f2e',
    colorBgContainer: '#242a3d',
    colorBgElevated: '#2d3448',
  },
  components: sharedComponents,
};
