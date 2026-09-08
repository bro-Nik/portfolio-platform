import { useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useOverviewQuery } from 'src/modules/portfolios/hooks/useOverviewQuery';
import { useTickerIds, extractTickerIds, useAssetPricesQuery } from 'src/hooks/TickerContext';
import { buildWalletStats } from 'src/utils/assetStats';

export const useWalletsData = (showArchived = false) => {
  const queryClient = useQueryClient();
  const { addTickerIds } = useTickerIds();

  const { data, isLoading } = useOverviewQuery();
  const rawWallets = data?.wallets || [];

  useEffect(() => {
    if (rawWallets.length > 0) {
      const ids = extractTickerIds(rawWallets);
      if (ids.length > 0) addTickerIds(ids);
    }
  }, [rawWallets, addTickerIds]);

  const internalPricesQuery = useAssetPricesQuery();
  const prices = useMemo(() =>
    internalPricesQuery.data?.prices || {},
    [internalPricesQuery.data]
  );
  const pricesLoading = internalPricesQuery.isLoading;

  const getWallet = (walletId) => {
    return rawWallets?.find(wallet => wallet.id === walletId) || null;
  };

  const { items: walletsWithStats, overall: overallStats } = useMemo(
    () => buildWalletStats(rawWallets, prices),
    [rawWallets, prices]
  );

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
