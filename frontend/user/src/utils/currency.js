import { getCurrencyRate, usePreferencesStore } from 'src/stores/preferencesStore';

export const useDisplayCurrency = () => usePreferencesStore((state) => state.displayCurrency);

const displayCurrencyRate = () => getCurrencyRate(usePreferencesStore.getState().displayCurrency);

export const fromUsd = (value) => {
  if (value == null) return value;
  return value / displayCurrencyRate();
};

export const toUsd = (value) => {
  if (value == null) return value;
  return value * displayCurrencyRate();
};
