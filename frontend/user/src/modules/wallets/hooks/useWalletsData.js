import { useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWalletsQuery } from './useWalletsQuery';
import { useTickerIds, extractTickerIds } from 'src/hooks/TickerContext';
import { useAssetPricesQuery } from 'src/hooks/TickerContext';

export const useWalletsData = () => {
  const queryClient = useQueryClient();
  const { addTickerIds } = useTickerIds();

  const { data, isLoading } = useWalletsQuery();
  const rawWallets = data?.wallets || [];

  useEffect(() => {
    if (rawWallets.length > 0) {
      const ids = extractTickerIds(rawWallets);
      if (ids.length > 0) addTickerIds(ids);
    }
  }, [rawWallets, addTickerIds]);

  const { data: pricesData } = useAssetPricesQuery();
  const prices = useMemo(() => pricesData?.prices || {}, [pricesData]);

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

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ['wallets'] });
  };

  return {
    wallets: walletsWithStats,
    overallStats,
    loading: isLoading,
    getWallet,
    refresh,
  };
};
