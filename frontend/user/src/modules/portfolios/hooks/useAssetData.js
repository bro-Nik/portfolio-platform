import { useMemo } from 'react';
import { usePortfolioAssetTransactionsQuery } from './usePortfolioAssetQuery';
import { sortTransactions } from 'src/modules/assets/utils/assetUtils'

export const useAssetData = (portfolio, asset, { enabled } = {}) => {
  const skip = asset?.hasTransactions === false;
  const { data: transactions, isLoading } = usePortfolioAssetTransactionsQuery(asset?.id, {
    enabled: enabled && !!asset?.id && !skip,
  });

  const assetData = useMemo(() => {
    if (!asset) return null;

    return {
      ...asset,
      share: portfolio?.costNow > 0 ? (asset.costNow / portfolio.costNow) * 100 : 0,
      free: asset.quantity - (asset.sellOrders || 0),
      transactions: skip ? [] : (transactions ? sortTransactions(transactions) : undefined),
    };
  }, [asset, transactions, portfolio?.costNow, skip]);

  return {
    loading: isLoading || !assetData,
    assetData,
  };
};
