import { useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useOverviewQuery } from './useOverviewQuery';
import { useTickerIds, extractTickerIds } from 'src/hooks/TickerContext';
import { useAssetPricesQuery } from 'src/hooks/TickerContext';

export const usePortfoliosData = (showArchived = false) => {
  const queryClient = useQueryClient();
  const { addTickerIds } = useTickerIds();

  const { data, isLoading } = useOverviewQuery();
  const rawPortfolios = data?.portfolios || [];

  useEffect(() => {
    if (rawPortfolios.length > 0) {
      const ids = extractTickerIds(rawPortfolios);
      if (ids.length > 0) addTickerIds(ids);
    }
  }, [rawPortfolios, addTickerIds]);

  const internalPricesQuery = useAssetPricesQuery();
  const prices = useMemo(() =>
    internalPricesQuery.data?.prices || {},
    [internalPricesQuery.data]
  );
  const pricesLoading = internalPricesQuery.isLoading;

  const { portfoliosWithStats, overallStats } = useMemo(() => {
    if (!rawPortfolios || rawPortfolios.length === 0) return { portfoliosWithStats: [], overallStats: {} };

    let totalCostNow = 0;
    let totalInvested = 0;
    let totalBuyOrders = 0;
    let totalProfit = 0;
    let totalCapitalDeployed = 0;

    const portfoliosWithStats = rawPortfolios.map(portfolio => {
      let costNow = 0;
      let invested = 0;
      let buyOrders = 0;
      let profit = 0;
      let capitalDeployed = 0;

      const assetsWithStats = portfolio.assets?.map(asset => {
        const assetQuantity = Number(asset.quantity) || 0;
        const assetAmount = Number(asset.amount) || 0;
        const assetBuyOrders = Number(asset.buyOrders) || 0;
        const assetRealizedProfit = Number(asset.realizedProfit) || 0;
        const assetTotalInvested = Number(asset.totalInvested) || 0;

        const price = prices[asset.tickerId] || 0;
        const assetCostNow = assetQuantity * price;
        const assetInvested = Math.max(0, assetAmount);
        const hasBasis = assetInvested > 0 || assetRealizedProfit !== 0;
        const assetAveragePrice = hasBasis && assetQuantity > 0 ? assetInvested / assetQuantity : null;
        const assetProfit = hasBasis ? assetCostNow - assetInvested + assetRealizedProfit : null;

        costNow += assetCostNow;
        invested += assetInvested;
        buyOrders += assetBuyOrders;
        profit += assetProfit ?? 0;
        capitalDeployed += assetTotalInvested;

        return {
          ...asset,
          costNow: assetCostNow,
          averagePrice: assetAveragePrice,
          invested: assetInvested,
          totalInvested: assetTotalInvested || assetInvested,
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
  }, [rawPortfolios, prices]);

  const filteredPortfolios = useMemo(() => {
    if (showArchived) return portfoliosWithStats;
    const active = portfoliosWithStats.filter(p => !p.isArchived);
    return active.length > 0 ? active : portfoliosWithStats.filter(p => p.isArchived);
  }, [portfoliosWithStats, showArchived]);

  const showingArchivedFallback = !showArchived && portfoliosWithStats.length > 0 && portfoliosWithStats.every(p => p.isArchived);

  const getPortfolio = (id) => rawPortfolios?.find(p => p.id === id);
  const getPortfolioAsset = (portfolio, id) => portfolio.assets?.find(a => a.id === id);

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ['overview'] });
  };

  return {
    portfolios: filteredPortfolios,
    allPortfolios: portfoliosWithStats,
    overallStats,
    loading: isLoading || pricesLoading,
    showingArchivedFallback,
    getPortfolio,
    getPortfolioAsset,
    refresh,
  };
};
