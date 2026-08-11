import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const usePreferencesStore = create()(
  persist(
    (set) => ({
      displayCurrency: 'USD',
      rates: {},
      setCurrency: (currency) => set({ displayCurrency: currency }),
      setRates: (rates) => set({ rates }),
    }),
    {
      name: 'app-preferences',
      partialize: (state) => ({ displayCurrency: state.displayCurrency }),
    }
  )
);

export const getCurrencyRate = (symbol) => {
  const rate = usePreferencesStore.getState().rates[symbol];
  return typeof rate === 'number' && rate > 0 ? rate : 1;
};
