import React, { memo, useMemo } from 'react';
import DataTable from '/app/src/features/tables/DataTable';
import { useNavigation } from '/app/src/hooks/useNavigation';
import { useTicker } from '/app/src/hooks/useTicker';
import AssetActionsDropdown from '../AssetActionsDropdown';
import {
  createCostColumn,
  createShareColumn,
  createBuyOrdersColumn,
  createSellOrdersColumn,
  createProfitColumn,
  createInvestedColumn,
  createAssetNameColumn,
  createQuantityColumn,
  createAveragePriceColumn,
  createActionsColumn
} from '/app/src/features/tables/tableColumns';

const WalletTable = memo(({ wallet, assets }) => {
  const { openItem } = useNavigation();
  const { getTicker } = useTicker();

  // Подготавливаем данные для таблицы
  const preparedAssets = useMemo(() => {
    if (!assets) return [];

    return assets.map(asset => {
      const ticker = getTicker(asset.tickerId);

      return {
        ...asset,
        share: wallet.costNow > 0 ? (asset.costNow / wallet.costNow) * 100 : 0,
        image: ticker?.image,
        name: ticker?.name,
        symbol: ticker?.symbol,
      };
    });
  }, [assets, wallet.costNow]);

  const columns = useMemo(() => [
    createAssetNameColumn(openItem, 'wallet_asset', wallet.id),
    createQuantityColumn((a) => a.symbol, (a) => !a.quantity),
    createCostColumn((a) => !a.quantity),
    createShareColumn((a) => !a.quantity),
    createBuyOrdersColumn((a) => !a.quantity && !a.buyOrders),
    createSellOrdersColumn((a) => !a.quantity && !a.sellOrders),
    createActionsColumn(({ row }) => <AssetActionsDropdown wallet={wallet} asset={row.original} btn='icon' />),
  ], [openItem, wallet]);

  return (
    <DataTable 
      data={preparedAssets}
      columnsConfig={columns}
      placeholder="Поиск по активам..."
      children={wallet.comment}
    />
  );
});

export default WalletTable;
