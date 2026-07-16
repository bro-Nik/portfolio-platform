import { useMemo } from 'react';
import { usePortfolioAssetTransactionsQuery } from 'src/hooks/queries/usePortfolioAssetQuery';
import { useTickerQueries } from 'src/hooks/queries/TickerContext';
import { sortTransactions } from 'src/modules/assets/utils/assetUtils'

export const useAssetData = (portfolio, asset) => {
  const { data: transactions, isLoading } = usePortfolioAssetTransactionsQuery(asset?.id);
  const { info } = useTickerQueries();

  const assetData = useMemo(() => {
    if (!asset || !transactions) return null;

    const ticker = info[asset.tickerId];
    return {
      ...asset,
      share: portfolio?.costNow > 0 ? (asset.costNow / portfolio.costNow) * 100 : 0,
      image: ticker?.image,
      name: ticker?.name,
      symbol: ticker?.symbol,
      free: asset.quantity - (asset.buyOrders || 0),
      transactions: sortTransactions(transactions),
    };
  }, [asset, transactions, portfolio?.costNow, info, portfolio?.costNow]);

  return {
    loading: isLoading || !assetData,
    assetData,
  };
};
