export const formatCurrency = (number, currency = 'USD', locale = 'ru-RU', dontRound=false) => {
  number = Number(number);
  if (isNaN(number)) return;

  const formatOptions = {};
  if (dontRound) {
    formatOptions.minimumFractionDigits = 0;
    formatOptions.maximumFractionDigits = (number.toString().split('.')[1] || '').length;
  }

  // Проверяем, является ли валюта валидной ISO 4217
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
      ...formatOptions,
    }).format(number);
    
  } catch (error) {
    // Если валюта не ISO 4217, просто выводим число и переданную валюту
    const formattedNumber = new Intl.NumberFormat(locale, {
      ...formatOptions,
    }).format(number);
    
    return `${formattedNumber} ${currency.toUpperCase()}`;
  }
};

export const formatPercentage = (value, decimals = 0) => {
  return `${Math.abs(+value.toFixed(+decimals))}%`;
};

export const formatProfit = (profit, invested, totalInvested) => {
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
  return new Intl.NumberFormat('ru-RU', options).format(number);
};

export const getTradingViewUrl = (symbol, tickerId) => {
  if (tickerId?.startsWith('cr-')) {
    return `https://www.tradingview.com/chart/?symbol=${symbol}USDT`
  }
  return `https://www.tradingview.com/chart/?symbol=${symbol}USD`
};
