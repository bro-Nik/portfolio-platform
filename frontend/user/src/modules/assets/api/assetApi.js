import { getMarket } from 'src/api';

const market = getMarket();

export const assetApi = {
  getTickersByMarket: (markets, search, page, pageSize = 20) =>
    market.searchTickersMarketApiTickersGet({
      markets,
      page,
      pageSize,
      ...(search ? { search } : {}),
    }),

  getPrices: (tickerIds) => market.getPricesMarketApiTickersPricesPost(tickerIds),
};
