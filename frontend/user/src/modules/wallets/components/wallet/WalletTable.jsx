import React, { memo, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { useNavigation } from 'src/hooks/useNavigation';
import { useTicker } from 'src/hooks/useTicker';
import AssetActionsDropdown from '../AssetActionsDropdown';
import TagFilter from 'src/modules/portfolios/components/TagFilter';
import { Input } from 'antd';
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
  const { getTicker } = useTicker();
  const [tagFilterIds, setTagFilterIds] = useState([]);
  const [search, setSearch] = useState('');

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
  }, [assets, wallet.costNow, getTicker]);

  const filteredAssets = useMemo(() => {
    let result = preparedAssets;
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
  }, [preparedAssets, tagFilterIds, search]);

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
      </div>

      {wallet.comment && (
        <div style={{ marginBottom: 12 }}>
          <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{wallet.comment}</span>
        </div>
      )}

      <DataTable
        data={filteredAssets}
        columnsConfig={columns}
        storageKey="wallet-table-sorting"
      />
    </>
  );
});

export default WalletTable;
