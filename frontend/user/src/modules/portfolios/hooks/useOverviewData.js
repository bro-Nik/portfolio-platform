import { useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useOverviewQuery } from './useOverviewQuery';
import { useTickerIds, extractTickerIds } from 'src/hooks/TickerContext';
import { useAssetPricesQuery } from 'src/hooks/TickerContext';

export const useOverviewData = () => {
  const queryClient = useQueryClient();
  const { addTickerIds } = useTickerIds();

  const { data, isLoading: overviewLoading } = useOverviewQuery();
  const rawPortfolios = data?.portfolios || [];
  const rawWallets = data?.wallets || [];

  useEffect(() => {
    if (rawPortfolios.length > 0) {
      const ids = extractTickerIds(rawPortfolios);
      if (ids.length > 0) addTickerIds(ids);
    }
  }, [rawPortfolios, addTickerIds]);

  const { data: pricesData, isLoading: pricesLoading } = useAssetPricesQuery();
  const prices = useMemo(() => pricesData?.prices || {}, [pricesData]);

  const { portfoliosWithStats, overallPortfolioStats } = useMemo(() => {
    if (!rawPortfolios || rawPortfolios.length === 0) return { portfoliosWithStats: [], overallPortfolioStats: {} };

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
      overallPortfolioStats: {
        totalCostNow,
        totalInvested,
        totalProfit,
        totalBuyOrders,
        totalCapitalDeployed,
      }
    };
  }, [rawPortfolios, prices]);

  const { walletsWithStats, overallWalletStats } = useMemo(() => {
    if (!rawWallets || rawWallets.length === 0) return { walletsWithStats: [], overallWalletStats: {} };

    let totalCostNow = 0;
    let totalBuyOrders = 0;

    const walletsWithStats = rawWallets.map(wallet => {
      let costNow = 0;
      let buyOrders = 0;

      const assetsWithStats = wallet.assets?.map(asset => {
        const assetQuantity = Number(asset.quantity) || 0;
        const assetBuyOrders = Number(asset.buyOrders) || 0;

        const price = prices[asset.tickerId] || 0;
        const assetCostNow = assetQuantity * price;

        costNow += assetCostNow;
        buyOrders += assetBuyOrders || 0;

        return {
          ...asset,
          costNow: assetCostNow,
          price
        };
      }) || [];

      totalCostNow += costNow;
      totalBuyOrders += buyOrders;

      return {
        ...wallet,
        assets: assetsWithStats,
        costNow,
        buyOrders,
      };
    });

    const walletsWithStatsAndShare = walletsWithStats.map(wallet => ({
      ...wallet,
      share: totalCostNow > 0 ? (wallet.costNow / totalCostNow) * 100 : 0
    }));

    return {
      walletsWithStats: walletsWithStatsAndShare,
      overallWalletStats: {
        totalCostNow,
        totalBuyOrders
      }
    };
  }, [rawWallets, prices]);

  const loading = overviewLoading || pricesLoading;

  const getPortfolio = (id) => rawPortfolios?.find(p => p.id === id);
  const getPortfolioAsset = (portfolio, id) => portfolio.assets?.find(a => a.id === id);
  const getWallet = (id) => rawWallets?.find(w => w.id === id);

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ['overview'] });
  };

  return {
    portfolios: portfoliosWithStats,
    wallets: walletsWithStats,
    allPortfolios: portfoliosWithStats,
    allWallets: walletsWithStats,
    portfolioStats: overallPortfolioStats,
    walletStats: overallWalletStats,
    loading,
    getPortfolio,
    getPortfolioAsset,
    getWallet,
    refresh,
  };
};
