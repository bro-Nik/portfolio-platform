import { useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useOverviewQuery } from './useOverviewQuery';
import { useTickerIds, extractTickerIds, useAssetPricesQuery } from 'src/hooks/TickerContext';
import { buildPortfolioStats, buildWalletStats } from 'src/utils/assetStats';

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

  const { items: portfoliosWithStats, overall: overallPortfolioStats } = useMemo(
    () => buildPortfolioStats(rawPortfolios, prices),
    [rawPortfolios, prices]
  );

  const { items: walletsWithStats, overall: overallWalletStats } = useMemo(
    () => buildWalletStats(rawWallets, prices),
    [rawWallets, prices]
  );

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
