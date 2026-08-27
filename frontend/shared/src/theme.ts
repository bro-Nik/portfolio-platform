import { theme } from 'antd';
import type { ThemeConfig } from 'antd';

export const darkBackgroundTokens = {
  colorBgLayout: '#1a1f2e',
  colorBgContainer: '#242a3d',
  colorBgElevated: '#2d3448',
} as const;

type ThemeToken = NonNullable<ThemeConfig['token']>;
type ThemeComponents = NonNullable<ThemeConfig['components']>;

export interface ThemeOverrides {
  tokens?: ThemeToken;
  components?: ThemeComponents;
}

export interface CreateThemesOptions extends ThemeOverrides {
  colorPrimary: string;
  borderRadius?: number;
  light?: ThemeOverrides;
  dark?: ThemeOverrides;
}

export interface AppThemes {
  lightTheme: ThemeConfig;
  darkTheme: ThemeConfig;
}

export function createThemes({
  colorPrimary,
  borderRadius,
  tokens,
  components,
  light,
  dark,
}: CreateThemesOptions): AppThemes {
  const baseToken: ThemeToken = {
    ...(borderRadius !== undefined ? { borderRadius } : {}),
    ...tokens,
    colorPrimary,
  };

  const lightTheme: ThemeConfig = {
    algorithm: theme.defaultAlgorithm,
    token: { ...baseToken, ...light?.tokens },
    components: { ...components, ...light?.components },
  };

  const darkTheme: ThemeConfig = {
    algorithm: theme.darkAlgorithm,
    token: { ...baseToken, ...darkBackgroundTokens, ...dark?.tokens },
    components: { ...components, ...dark?.components },
  };

  return { lightTheme, darkTheme };
}
