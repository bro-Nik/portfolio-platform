import React, { memo, useMemo, useState } from 'react';
import DataTable from '/app/src/features/tables/DataTable';
import { useNavigation } from '/app/src/hooks/useNavigation';
import { useTicker } from '/app/src/hooks/useTicker';
import AssetActionsDropdown from '../AssetActionsDropdown';
import TagFilter from '/app/src/modules/portfolios/components/TagFilter';
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

const WalletTable = memo(({ wallet, assets, onRefresh }) => {
  const { openItem } = useNavigation();
  const { getTicker } = useTicker();
  const [tagFilterIds, setTagFilterIds] = useState([]);

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

  const filteredAssets = useMemo(() => {
    if (tagFilterIds.length === 0) return preparedAssets;
    return preparedAssets.filter(asset =>
      asset.tags?.some(t => tagFilterIds.includes(t.id))
    );
  }, [preparedAssets, tagFilterIds]);

  const columns = useMemo(() => [
    createAssetNameColumn(openItem, 'wallet_asset', wallet.id),
    createQuantityColumn((a) => a.symbol, (a) => !a.quantity),
    createCostColumn((a) => !a.quantity),
    createShareColumn((a) => !a.quantity),
    createBuyOrdersColumn((a) => !a.quantity && !a.buyOrders),
    createSellOrdersColumn((a) => !a.quantity && !a.sellOrders),
    createActionsColumn(({ row }) => <AssetActionsDropdown wallet={wallet} asset={row.original} btn='icon' onUpdate={onRefresh} />),
  ], [openItem, wallet, onRefresh]);

  return (
    <DataTable 
      data={filteredAssets}
      columnsConfig={columns}
      placeholder="Поиск по активам..."
      storageKey="wallet-table-sorting"
    >
      <div className="d-flex align-items-center gap-3 flex-wrap mt-1">
        {wallet.comment && (
          <span className="text-muted small">{wallet.comment}</span>
        )}
        <TagFilter onChange={setTagFilterIds} />
      </div>
    </DataTable>
  );
});

export default WalletTable;
