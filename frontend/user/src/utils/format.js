const currencyFormatCache = {};

function getCachedFormatter(locale, currency, formatOptions) {
  if (formatOptions && Object.keys(formatOptions).length > 0) {
    return new Intl.NumberFormat(locale, { style: 'currency', currency, ...formatOptions });
  }
  const key = `${locale}:${currency}`;
  if (!currencyFormatCache[key]) {
    currencyFormatCache[key] = new Intl.NumberFormat(locale, { style: 'currency', currency });
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
  number = Number(number);
  if (isNaN(number)) return;

  const formatOptions = {};
  if (dontRound) {
    formatOptions.minimumFractionDigits = 0;
    formatOptions.maximumFractionDigits = (number.toString().split('.')[1] || '').length;
  }

  try {
    const formatter = formatOptions && Object.keys(formatOptions).length > 0
      ? new Intl.NumberFormat(locale, { style: 'currency', currency, ...formatOptions })
      : getCachedFormatter(locale, currency, null);
    return formatter.format(number);

  } catch {
    const formatter = getCachedNumberFormatter(locale, formatOptions);
    return `${formatter.format(number)} ${currency.toUpperCase()}`;
  }
};

export const formatPercentage = (value, decimals = 0) => {
  return `${Math.abs(+value.toFixed(+decimals))}%`;
};

export const formatProfit = (profit, invested, totalInvested) => {
  if (profit == null) return;
  profit = Number(profit);
  invested = Number(invested);
  if (isNaN(profit) || isNaN(invested)) return;

  const base = totalInvested !== undefined ? Number(totalInvested) : invested;
  const percentage = base === 0 ? 0 : (profit / base) * 100;
  let profitStr = formatCurrency(profit);
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
