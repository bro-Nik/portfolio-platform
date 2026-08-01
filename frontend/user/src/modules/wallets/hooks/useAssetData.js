import { useMemo } from 'react';
import { useWalletAssetTransactionsQuery } from './useWalletAssetQuery';
import { sortTransactions } from 'src/modules/assets/utils/assetUtils'

export const useAssetData = (wallet, asset, { enabled } = {}) => {
  const skip = asset?.hasTransactions === false;
  const { data: transactions, isLoading } = useWalletAssetTransactionsQuery(asset?.id, {
    enabled: enabled && !!asset?.id && !skip,
  });

  const assetData = useMemo(() => {
    if (!asset) return null;

    return {
      ...asset,
      share: wallet?.costNow > 0 ? (asset.costNow / wallet.costNow) * 100 : 0,
      free: asset.quantity - (asset.buyOrders || 0),
      transactions: skip ? [] : (transactions ? sortTransactions(transactions) : undefined),
    };
  }, [asset, transactions, wallet?.costNow, skip]);

  return {
    loading: isLoading || !assetData,
    assetData,
  };
};
