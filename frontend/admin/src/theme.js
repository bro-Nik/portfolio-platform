import { createThemes } from '@portfolio/shared';

const sharedComponents = {
  Alert: {
    lineWidth: 0,
  },
  Button: {
    colorBorderDisabled: 'transparent',
  },
};

const { lightTheme, darkTheme } = createThemes({
  colorPrimary: '#1890ff',
  borderRadius: 6,
  components: sharedComponents,
});

export { lightTheme, darkTheme };
