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
    let totalCapitalDeployed = 0;
    
    // Расчет статистики для каждого портфеля
    const portfoliosWithStats = portfolios.map(portfolio => {
      let costNow = 0;
      let invested = 0;
      let buyOrders = 0;
      let profit = 0;
      let capitalDeployed = 0;

      // Расчет статистики для каждого актива
      const assetsWithStats = portfolio.assets?.map(asset => {
        const assetQuantity = Number(asset.quantity) || 0;
        const assetAmount = Number(asset.amount) || 0;
        const assetBuyOrders = Number(asset.buyOrders) || 0;
        const assetRealizedProfit = Number(asset.realizedProfit) || 0;
        const assetTotalInvested = Number(asset.totalInvested) || 0;

        const price = prices[asset.tickerId] || 0;
        const assetCostNow = assetQuantity * price;
        const assetInvested = Math.max(0, assetAmount);
        const assetAveragePrice = assetQuantity > 0 ? assetInvested / assetQuantity : 0;
        const assetProfit = assetCostNow - assetInvested + assetRealizedProfit;

        costNow += assetCostNow;
        invested += Math.max(0, assetAmount);
        buyOrders += assetBuyOrders;
        profit += assetProfit;
        capitalDeployed += assetTotalInvested;

        return {
          ...asset,
          costNow: assetCostNow,
          averagePrice: assetAveragePrice,
          invested: Math.max(0, assetAmount),
          totalInvested: assetTotalInvested || Math.max(0, assetAmount),
          realizedProfit: assetRealizedProfit,
          profit: assetProfit,
          price
        };
      }) || [];

      totalCostNow += costNow;
      totalInvested += invested;
      totalBuyOrders += buyOrders;
      totalProfit += profit;
      totalCapitalDeployed += capitalDeployed;

      return {
        ...portfolio,
        assets: assetsWithStats,
        costNow,
        invested,
        totalInvested: capitalDeployed,
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
        totalBuyOrders,
        totalCapitalDeployed,
      }
    };
  }, [portfolios, prices]);

  const getPortfolio = (id) => portfolios?.find(p => p.id === id);
  const getPortfolioAsset = (portfolio, id) => portfolio.assets?.find(a => a.id === id);

  const refresh = async () => {
    setLoading(true);
    const result = await portfolioApi.getPortfolios();
    if (result.success) setPortfolios(result.data.portfolios || []);
    setLoading(false);
  };

  return {
    // Данные с расчетами
    portfolios: portfoliosWithStats,
    overallStats,

    // Состояние
    loading,

    // Методы
    getPortfolio,
    getPortfolioAsset,
    refresh,
  };
};
