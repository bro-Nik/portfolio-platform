import React, { memo, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { useNavigation } from 'src/hooks/useNavigation';
import { useLocalStorage } from 'src/hooks/useLocalStorage';
import AssetActionsDropdown from '../AssetActionsDropdown';
import TagFilter from '../TagFilter';
import { Alert, Checkbox, Input } from 'antd';
import {
  createCostColumn,
  createShareColumn,
  createBuyOrdersColumn,
  createProfitColumn,
  createInvestedColumn,
  createAssetNameColumn,
  createQuantityColumn,
  createAveragePriceColumn,
  createActionsColumn
} from 'src/features/tables/tableColumns';

const PortfolioTable = memo(({ portfolio, assets, onRefresh }) => {
  const { openItem } = useNavigation();

  const [hideCheap, setHideCheap] = useLocalStorage('portfolio-hide-cheap', false);
  const [showArchived, setShowArchived] = useLocalStorage('portfolio-archive', false);
  const [tagFilterIds, setTagFilterIds] = useState([]);
  const [search, setSearch] = useState('');

  // Подготавливаем данные для таблицы
  const preparedAssets = useMemo(() => {
    if (!assets) return [];

    return assets.map(asset => {
      return {
        ...asset,
        share: portfolio.costNow > 0 ? (asset.costNow / portfolio.costNow) * 100 : 0,
        symbol: asset.symbol?.toUpperCase(),
      };
    });
  }, [assets, portfolio.costNow]);

  const filteredAssets = useMemo(() => {
    let result = preparedAssets;
    if (hideCheap) result = result.filter(asset => asset.costNow >= 1);
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
  }, [preparedAssets, hideCheap, showArchived, tagFilterIds, search]);

  const showingArchivedFallback = !showArchived && preparedAssets.length > 0 && preparedAssets.every(a => a.isArchived);

  const columns = useMemo(() => [
    createAssetNameColumn(openItem, 'portfolio_asset', portfolio.id),
    createQuantityColumn((a) => a.symbol, (a) => !a.quantity),
    createAveragePriceColumn((a) => !a.averagePrice),
    createCostColumn((a) => !a.quantity),
    createInvestedColumn((a) => !a.quantity),
    createProfitColumn((a) => !a.quantity),
    createShareColumn((a) => !a.quantity),
    createBuyOrdersColumn((a) => !a.quantity && !a.buyOrders),
    createActionsColumn(({ row }) => <AssetActionsDropdown portfolio={portfolio} asset={row.original} btn='icon' onUpdate={onRefresh} />),
  ], [openItem, portfolio, onRefresh]);

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
        <Checkbox checked={hideCheap} onChange={(e) => setHideCheap(e.target.checked)}>
          Спрятать дешевле $1
        </Checkbox>
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

      {portfolio.comment && (
        <div style={{ marginBottom: 12 }}>
          <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{portfolio.comment}</span>
        </div>
      )}

      <DataTable
        data={filteredAssets}
        columnsConfig={columns}
        storageKey="portfolio-table-sorting"
        rowClassName={(record) => record.isArchived ? 'archived-row' : ''}
      />
    </>
  );
});

export default PortfolioTable;
