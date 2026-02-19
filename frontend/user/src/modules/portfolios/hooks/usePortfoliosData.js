import { useEffect, useMemo, useRef, useState } from 'react';
import { portfolioApi } from '../api/portfolioApi';
import { useDataStore } from '/app/src/stores/dataStore';

export const usePortfoliosData = () => {
  const [loading, setLoading] = useState(false);

  const portfolios = useDataStore(state => state.portfolios);
  const prices = useDataStore(state => state.assetPrices);
  const setPortfolios = useDataStore(state => state.setPortfolios);

  // Отслеживание первоначальной загрузки
  const initialLoadRef = useRef(false);

  useEffect(() => {
    const fetchInitialData = async () => {
      initialLoadRef.current = true;
      setLoading(true);
      const result = await portfolioApi.getPortfolios();
      if (result.success) setPortfolios(result.data.portfolios || []);
      setLoading(false);
    };

    // Загружаем только один раз
    if (portfolios.length === 0 && !initialLoadRef.current) fetchInitialData();
  }, [portfolios.length, setPortfolios]);

  // Расчет статистики
  const { portfoliosWithStats, overallStats } = useMemo(() => {
    if (portfolios === null || portfolios.length === 0) return { portfoliosWithStats: [], overallStats: {} };

    let totalCostNow = 0;
    let totalInvested = 0;
    let totalBuyOrders = 0;
    let totalProfit = 0;
    
    // Расчет статистики для каждого портфеля
    const portfoliosWithStats = portfolios.map(portfolio => {
      let costNow = 0;
      let invested = 0;
      let buyOrders = 0;
      let profit = 0;

      // Расчет статистики для каждого актива
      const assetsWithStats = portfolio.assets?.map(asset => {
        const assetQuantity = Number(asset.quantity) || 0;
        const assetAmount = Number(asset.amount) || 0;
        const assetBuyOrders = Number(asset.buyOrders) || 0;

        const price = prices[asset.tickerId] || 0;
        const assetCostNow = assetQuantity * price;
        const assetInvested = assetAmount;
        const assetAveragePrice = assetInvested / assetQuantity;
        const assetProfit = assetAveragePrice ? assetCostNow - assetInvested : 0;

        costNow += assetCostNow;
        invested += assetInvested;
        buyOrders += assetBuyOrders;
        profit += assetProfit;

        return {
          ...asset,
          costNow: assetCostNow,
          averagePrice: assetAveragePrice,
          invested: assetInvested,
          profit: assetProfit,
          price
        };
      }) || [];

      totalCostNow += costNow;
      totalInvested += invested;
      totalBuyOrders += buyOrders;
      totalProfit += profit;

      return {
        ...portfolio,
        assets: assetsWithStats,
        costNow,
        invested,
        buyOrders,
        profit,
      };
    });

    const portfoliosWithStatsAndShare = portfoliosWithStats.map(portfolio => ({
      ...portfolio,
      share: totalInvested > 0 ? (portfolio.invested / totalInvested) * 100 : 0
    }));

    return {
      portfoliosWithStats: portfoliosWithStatsAndShare,
      overallStats: {
        totalCostNow,
        totalInvested,
        totalProfit,
        totalBuyOrders
      }
    };
  }, [portfolios, prices]);

  const getPortfolio = (id) => portfolios?.find(p => p.id === id);
  const getPortfolioAsset = (portfolio, id) => portfolio.assets?.find(a => a.id === id);

  return {
    // Данные с расчетами
    portfolios: portfoliosWithStats,
    overallStats,

    // Состояние
    loading,

    // Методы
    getPortfolio,
    getPortfolioAsset,
  };
};
