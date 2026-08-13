import { fromUsd } from 'src/utils/currency';
import { usePreferencesStore } from 'src/stores/preferencesStore';

const currencyFormatCache = {};

function getCachedFormatter(locale, currency, formatOptions) {
  const key = `${locale}:${currency}:${formatOptions ? JSON.stringify(formatOptions) : 'default'}`;
  if (!currencyFormatCache[key]) {
    currencyFormatCache[key] = new Intl.NumberFormat(locale, { style: 'currency', currency, ...(formatOptions || {}) });
  }
  return currencyFormatCache[key];
}

const numberFormatCache = {};

function getCachedNumberFormatter(locale, formatOptions) {
  const key = `${locale}:${JSON.stringify(formatOptions)}`;
  if (!numberFormatCache[key]) {
    numberFormatCache[key] = new Intl.NumberFormat(locale, formatOptions);
  }
  return numberFormatCache[key];
}

export const formatCurrency = (number, currency = 'USD', locale = 'ru-RU', dontRound=false) => {
  if (number == null) return '-';
  number = Number(number);
  if (isNaN(number)) return '-';
  if (number === 0) number = 0;

  if (!dontRound) {
    number = Math.floor(number);
  }

  const formatOptions = {};
  if (dontRound) {
    formatOptions.minimumFractionDigits = 0;
    formatOptions.maximumFractionDigits = (number.toString().split('.')[1] || '').length;
  } else {
    formatOptions.minimumFractionDigits = 0;
    formatOptions.maximumFractionDigits = 0;
  }

  try {
    const formatter = getCachedFormatter(locale, currency, formatOptions);
    return formatter.format(number);

  } catch {
    const formatter = getCachedNumberFormatter(locale, formatOptions);
    return `${formatter.format(number)} ${currency.toUpperCase()}`;
  }
};

export const formatPercentage = (value, decimals = 0) => {
  return `${Math.abs(+value.toFixed(+decimals))}%`;
};

export const formatCurrencyFromUsd = (number, dontRound = false) => {
  if (number == null) return formatCurrency(number);
  const { displayCurrency } = usePreferencesStore.getState();
  const value = fromUsd(number);
  if (dontRound) return formatCurrency(value, displayCurrency, 'ru-RU', true);
  const rounded = number >= 0 && number < 1 ? Math.floor(value) : Math.round(value);
  return formatCurrency(rounded, displayCurrency, 'ru-RU', true);
};

export const formatUsdValueOrDash = (number, dontRound = false) => {
  if (number == null || Number(number) <= 0) return '-';
  const value = formatCurrencyFromUsd(number, dontRound);
  return value === formatCurrencyFromUsd(0, dontRound) ? '-' : value;
};

export const formatProfit = (profit, invested, totalInvested) => {
  if (profit == null) return;
  profit = Number(profit);
  invested = Number(invested);
  if (isNaN(profit) || isNaN(invested)) return;

  const base = totalInvested !== undefined ? Number(totalInvested) : invested;
  const percentage = base === 0 ? 0 : (profit / base) * 100;
  let profitStr = formatCurrencyFromUsd(profit);
  if (percentage) profitStr += ` (${formatPercentage(percentage)})`;
  return profitStr;
};

export const getColorClass = (number) => {
  number = Number(number);
  if (isNaN(number)) number = 0;

  if (number > 0) return 'text-green';
  if (number < 0) return 'text-red';
  return '';
};

export const formatNumber = (number, options = {}) => {
  const formatter = getCachedNumberFormatter('ru-RU', options);
  return formatter.format(number);
};

export const formatQuantity = (value) => {
  const number = Number(value);
  if (value == null || Number.isNaN(number)) return '0';
  if (number === 0) return '0';
  return number.toLocaleString('ru-RU', { maximumFractionDigits: 17 });
};

export const formatDateTime = (date) => {
  if (!date) return '-';
  return new Date(date).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getTradingViewUrl = (symbol, market) => {
  if (market === 'crypto') {
    return `https://www.tradingview.com/chart/?symbol=${symbol}USDT`
  }
  return `https://www.tradingview.com/chart/?symbol=${symbol}USD`
};
