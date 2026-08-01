import { useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useOverviewQuery } from 'src/modules/portfolios/hooks/useOverviewQuery';
import { useAssetPricesQuery } from 'src/hooks/TickerContext';

export const useWalletsData = (showArchived = false) => {
  const queryClient = useQueryClient();

  const { data, isLoading } = useOverviewQuery();
  const rawWallets = data?.wallets || [];

  const internalPricesQuery = useAssetPricesQuery();
  const prices = useMemo(() =>
    internalPricesQuery.data?.prices || {},
    [internalPricesQuery.data]
  );
  const pricesLoading = internalPricesQuery.isLoading;

  const getWallet = (walletId) => {
    return rawWallets?.find(wallet => wallet.id === walletId) || null;
  };

  const { walletsWithStats, overallStats } = useMemo(() => {
    if (!rawWallets || rawWallets.length === 0) return { walletsWithStats: [], overallStats: {} };

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
      overallStats: {
        totalCostNow,
        totalBuyOrders
      }
    };
  }, [rawWallets, prices]);

  const filteredWallets = useMemo(() => {
    if (showArchived) return walletsWithStats;
    const active = walletsWithStats.filter(w => !w.isArchived);
    return active.length > 0 ? active : walletsWithStats.filter(w => w.isArchived);
  }, [walletsWithStats, showArchived]);

  const showingArchivedFallback = !showArchived && walletsWithStats.length > 0 && walletsWithStats.every(w => w.isArchived);

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ['overview'] });
  };

  return {
    wallets: filteredWallets,
    allWallets: walletsWithStats,
    overallStats,
    loading: isLoading || pricesLoading,
    showingArchivedFallback,
    getWallet,
    refresh,
  };
};
