import { useDataStore } from '/app/src/stores/dataStore';

export const useTicker = () => {
  const tickers = useDataStore(state => state.assetInfo);
  const prices = useDataStore(state => state.assetPrices);

  const getTicker = (tickerId) => {
    if (!tickerId) return null;

    const ticker = tickers[tickerId];
    if (!ticker) return null;

    return {
      ...ticker,
      id: tickerId,
      symbol: ticker.symbol?.toUpperCase(), 
      price: getTickerPrice(tickerId)
    };
  };

  const getTickerSymbol = (tickerId) => {
    return tickers[tickerId]?.symbol?.toUpperCase();
  };

  const getTickerPrice = (tickerId) => {
    return prices[tickerId] || 0;
  };
  
  return {
    tickers,
    getTicker,
    getTickerSymbol,
    getTickerPrice
  };
};
