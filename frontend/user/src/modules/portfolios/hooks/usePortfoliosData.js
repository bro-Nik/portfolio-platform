import { useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useOverviewQuery } from './useOverviewQuery';
import { useTickerIds, extractTickerIds, useAssetPricesQuery } from 'src/hooks/TickerContext';
import { buildPortfolioStats } from 'src/utils/assetStats';

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

  const { items: portfoliosWithStats, overall: overallStats } = useMemo(
    () => buildPortfolioStats(rawPortfolios, prices),
    [rawPortfolios, prices]
  );

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
