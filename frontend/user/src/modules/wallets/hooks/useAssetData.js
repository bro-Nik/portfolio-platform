import { useMemo } from 'react';
import { useWalletAssetTransactionsQuery } from './useWalletAssetQuery';
import { useTickerQueries } from 'src/hooks/TickerContext';
import { sortTransactions } from 'src/modules/assets/utils/assetUtils'

export const useAssetData = (wallet, asset) => {
  const { data: transactions, isLoading } = useWalletAssetTransactionsQuery(asset?.id);
  const { info } = useTickerQueries();

  const assetData = useMemo(() => {
    if (!asset || !transactions) return null;

    const ticker = info[asset.tickerId];
    return {
      ...asset,
      share: wallet?.costNow > 0 ? (asset.costNow / wallet.costNow) * 100 : 0,
      image: ticker?.image,
      name: ticker?.name,
      symbol: ticker?.symbol,
      free: asset.quantity - (asset.buyOrders || 0),
      transactions: sortTransactions(transactions),
    };
  }, [asset, transactions, wallet?.costNow, info]);

  return {
    loading: isLoading || !assetData,
    assetData,
  };
};
