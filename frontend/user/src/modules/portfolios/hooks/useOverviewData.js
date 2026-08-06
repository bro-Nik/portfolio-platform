import { useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useOverviewQuery } from './useOverviewQuery';
import { useTickerIds, extractTickerIds } from 'src/hooks/TickerContext';
import { useAssetPricesQuery } from 'src/hooks/TickerContext';
import { calculatePortfolioAssetStats, calculateWalletAssetStats } from 'src/utils/assetStats';

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
        const price = prices[asset.tickerId];
        const stats = calculatePortfolioAssetStats(asset, price);

        costNow += stats.costNow || 0;
        invested += stats.invested;
        buyOrders += stats.buyOrders;
        profit += stats.profit ?? 0;
        capitalDeployed += stats.totalInvested;

        return {
          ...asset,
          ...stats,
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
        const price = prices[asset.tickerId] || 0;
        const stats = calculateWalletAssetStats(asset, price);

        costNow += stats.costNow;
        buyOrders += stats.buyOrders;

        return {
          ...asset,
          ...stats,
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
