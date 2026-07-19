import React, { memo, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { useNavigation } from 'src/hooks/useNavigation';
import { useLocalStorage } from 'src/hooks/useLocalStorage';
import AssetActionsDropdown from '../AssetActionsDropdown';
import TagFilter from 'src/modules/portfolios/components/TagFilter';
import { Alert, Input, Checkbox } from 'antd';
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
} from 'src/features/tables/tableColumns';

const WalletTable = memo(({ wallet, assets, onRefresh }) => {
  const { openItem } = useNavigation();
  const [tagFilterIds, setTagFilterIds] = useState([]);
  const [search, setSearch] = useState('');
  const [showArchived, setShowArchived] = useLocalStorage('wallet-archive', false);

  // Подготавливаем данные для таблицы
  const preparedAssets = useMemo(() => {
    if (!assets) return [];

    return assets.map(asset => {
      return {
        ...asset,
        share: wallet.costNow > 0 ? (asset.costNow / wallet.costNow) * 100 : 0,
        symbol: asset.symbol?.toUpperCase(),
      };
    });
  }, [assets, wallet.costNow]);

  const filteredAssets = useMemo(() => {
    let result = preparedAssets;
    if (!showArchived) {
      const active = result.filter(asset => !asset.isArchived);
      if (active.length > 0) result = active;
    }
    if (tagFilterIds.length > 0) {
      result = result.filter(asset =>
        asset.tags?.some(t => tagFilterIds.includes(t.id))
      );
    }
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(asset =>
        (asset.name && asset.name.toLowerCase().includes(q)) ||
        (asset.symbol && asset.symbol.toLowerCase().includes(q))
      );
    }
    return result;
  }, [preparedAssets, showArchived, tagFilterIds, search]);

  const showingArchivedFallback = !showArchived && preparedAssets.length > 0 && preparedAssets.every(a => a.isArchived);

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
    <>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 16 }}>
        <Input
          placeholder="Поиск..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          allowClear
          style={{ width: 160 }}
        />
        <TagFilter onChange={setTagFilterIds} />
        <Checkbox checked={showArchived} onChange={(e) => setShowArchived(e.target.checked)}>
          Показывать архивные
        </Checkbox>
      </div>

      {showingArchivedFallback && (
        <Alert
          message="Нет активных активов — показаны архивные"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {wallet.comment && (
        <div style={{ marginBottom: 12 }}>
          <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{wallet.comment}</span>
        </div>
      )}

      <DataTable
        data={filteredAssets}
        columnsConfig={columns}
        storageKey="wallet-table-sorting"
        rowClassName={(record) => record.isArchived ? 'archived-row' : ''}
      />
    </>
  );
});

export default WalletTable;
