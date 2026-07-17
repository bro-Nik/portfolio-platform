import { useMemo } from 'react';
import { usePortfolioAssetTransactionsQuery } from './usePortfolioAssetQuery';
import { sortTransactions } from 'src/modules/assets/utils/assetUtils'

export const useAssetData = (portfolio, asset) => {
  const { data: transactions, isLoading } = usePortfolioAssetTransactionsQuery(asset?.id);

  const assetData = useMemo(() => {
    if (!asset || !transactions) return null;

    return {
      ...asset,
      share: portfolio?.costNow > 0 ? (asset.costNow / portfolio.costNow) * 100 : 0,
      free: asset.quantity - (asset.buyOrders || 0),
      transactions: sortTransactions(transactions),
    };
  }, [asset, transactions, portfolio?.costNow]);

  return {
    loading: isLoading || !assetData,
    assetData,
  };
};
