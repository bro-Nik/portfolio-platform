import { useCallback, useMemo } from 'react';
import { useAssetPricesQuery, useAssetInfoQuery } from './queries/TickerContext';

export const useTicker = () => {
  const { data: pricesData } = useAssetPricesQuery();
  const { data: infoData } = useAssetInfoQuery();

  const prices = useMemo(() => pricesData?.prices || {}, [pricesData]);
  const tickers = useMemo(() => infoData?.info || {}, [infoData]);

  const getTicker = useCallback((tickerId) => {
    if (!tickerId) return null;

    const ticker = tickers[tickerId];
    if (!ticker) return null;

    return {
      ...ticker,
      id: tickerId,
      symbol: ticker.symbol?.toUpperCase(),
      price: prices[tickerId] || 0
    };
  }, [tickers, prices]);

  const getTickerSymbol = useCallback((tickerId) => {
    return tickers[tickerId]?.symbol?.toUpperCase();
  }, [tickers]);

  const getTickerPrice = useCallback((tickerId) => {
    return prices[tickerId] || 0;
  }, [prices]);

  return {
    tickers,
    getTicker,
    getTickerSymbol,
    getTickerPrice
  };
};
