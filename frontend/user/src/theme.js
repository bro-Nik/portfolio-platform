import { createThemes } from '@portfolio/shared';

const colorPrimary = '#6366f1';

const sharedTokens = {
  fontSize: 14,
  colorBgSpotlight: colorPrimary,
};

const sharedComponents = {
  Button: {
    borderRadius: 8,
    controlHeight: 36,
    borderRadiusLG: 10,
    colorBorderDisabled: 'transparent',
  },
  Card: {
    borderRadius: 12,
  },
  Modal: {
    borderRadius: 12,
  },
  Input: {
    borderRadius: 8,
    controlHeight: 36,
  },
  InputNumber: {
    borderRadius: 8,
    controlHeight: 36,
    colorBorderDisabled: 'transparent',
  },
  Select: {
    borderRadius: 8,
    controlHeight: 36,
    colorBorderDisabled: 'transparent',
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
  Alert: {
    lineWidth: 0,
  },
  TimePicker: {
    controlHeight: 36,
  },
  Segmented: {
    controlHeight: 36,
    itemHoverBg: 'transparent',
    itemActiveBg: 'transparent',
  },
};

const { lightTheme, darkTheme } = createThemes({
  colorPrimary,
  tokens: sharedTokens,
  components: sharedComponents,
  light: {
    tokens: {
      colorBgLayout: '#ffffff',
      colorBgContainer: '#ffffff',
    },
    components: {
      Segmented: {
        ...sharedComponents.Segmented,
        trackBg: '#f5f5f5',
      },
    },
  },
});

export { lightTheme, darkTheme };
