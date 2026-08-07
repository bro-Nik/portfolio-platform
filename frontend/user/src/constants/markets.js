export const MARKETS = [
  { value: 'crypto', label: 'Крипто' },
  { value: 'stocks', label: 'Акции' },
  { value: 'currency', label: 'Валюта' },
];

export const getMarketLabel = (value) => {
  return MARKETS.find(m => m.value === value)?.label ?? value;
};
