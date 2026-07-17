import { useMemo } from 'react';
import { useWalletAssetTransactionsQuery } from './useWalletAssetQuery';
import { sortTransactions } from 'src/modules/assets/utils/assetUtils'

export const useAssetData = (wallet, asset) => {
  const { data: transactions, isLoading } = useWalletAssetTransactionsQuery(asset?.id);

  const assetData = useMemo(() => {
    if (!asset || !transactions) return null;

    return {
      ...asset,
      share: wallet?.costNow > 0 ? (asset.costNow / wallet.costNow) * 100 : 0,
      free: asset.quantity - (asset.buyOrders || 0),
      transactions: sortTransactions(transactions),
    };
  }, [asset, transactions, wallet?.costNow]);

  return {
    loading: isLoading || !assetData,
    assetData,
  };
};
