import { useEffect, useState } from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Theme = 'light' | 'dark' | 'system';

export type ResolvedTheme = 'light' | 'dark';

const systemThemeOrder: Theme[] = ['light', 'dark', 'system'];

interface ThemeState {
  theme: Theme;
  getSystemTheme: () => ResolvedTheme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: 'light',
      getSystemTheme: () =>
        typeof window !== 'undefined' &&
        window.matchMedia?.('(prefers-color-scheme: dark)')?.matches
          ? 'dark'
          : 'light',
      toggleTheme: () =>
        set((state) => {
          const currentIndex = systemThemeOrder.indexOf(state.theme);
          const nextIndex = (currentIndex + 1) % systemThemeOrder.length;
          return { theme: systemThemeOrder[nextIndex] };
        }),
      setTheme: (theme: Theme) => set({ theme }),
    }),
    { name: 'app-theme' }
  )
);

export const useResolvedTheme = (): ResolvedTheme => {
  const theme = useThemeStore((state) => state.theme);
  const getSystemTheme = useThemeStore((state) => state.getSystemTheme);

  const [systemTheme, setSystemTheme] = useState<ResolvedTheme>(getSystemTheme);

  useEffect(() => {
    if (theme !== 'system') return;

    const media = window.matchMedia?.('(prefers-color-scheme: dark)');
    if (!media) return;

    const handler = () => setSystemTheme(media.matches ? 'dark' : 'light');
    handler();
    media.addEventListener('change', handler);
    return () => media.removeEventListener('change', handler);
  }, [theme]);

  return theme === 'system' ? systemTheme : theme;
};
