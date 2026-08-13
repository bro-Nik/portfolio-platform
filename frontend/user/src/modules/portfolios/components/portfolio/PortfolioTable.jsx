import { memo, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { useNavigation } from 'src/hooks/useNavigation';
import { usePersistedState } from '@portfolio/shared';
import AssetActionsDropdown from '../AssetActionsDropdown';
import TagFilter from 'src/modules/tags/components/TagFilter';
import { Alert } from '@portfolio/shared';
import { Checkbox, Input } from 'antd';
import { formatCurrency, formatCurrencyFromUsd, formatProfit, formatPercentage, formatQuantity, formatUsdValueOrDash, getColorClass } from 'src/utils/format';
import { calculatePortfolioAssetStats } from 'src/utils/assetStats';
import { useDisplayCurrency } from 'src/utils/currency';
import { createAssetNameColumn } from 'src/features/tables/tableColumns';

const DEFAULT_VALUE = '-';

const PortfolioTable = memo(({ portfolio, assets, onRefresh }) => {
  const { openItem } = useNavigation();
  const displayCurrency = useDisplayCurrency();

  const [hideCheap, setHideCheap] = usePersistedState('portfolio-hide-cheap', false);
  const [showArchived, setShowArchived] = usePersistedState('portfolio-archive', false);
  const [tagFilterIds, setTagFilterIds] = useState([]);
  const [search, setSearch] = useState('');

  // Подготавливаем данные для таблицы
  const preparedAssets = useMemo(() => {
    if (!assets) return [];

    return assets.map(asset => {
      const assetQuantity = Number(asset.quantity) || 0;
      const price = asset.price ?? null;
      const stats = calculatePortfolioAssetStats(asset, price);
      const symbol = asset.symbol?.toUpperCase();
      const share = portfolio.costNow > 0 ? ((asset.costNow || 0) / portfolio.costNow) * 100 : 0;
      const hasBasis = stats.hasBasis;

      return {
        ...asset,
        share,
        symbol,
        ...stats,
        invested: stats.invested,
        totalInvested: stats.totalInvested || stats.invested,
        _quantity: assetQuantity > 0 ? `${formatQuantity(assetQuantity)}${symbol ? ' ' : ''}${symbol ?? ''}` : DEFAULT_VALUE,
        _avgPrice: stats.averagePrice == null ? DEFAULT_VALUE : formatCurrencyFromUsd(stats.averagePrice, true),
        _cost: stats.costNow == null ? DEFAULT_VALUE : formatUsdValueOrDash(stats.costNow),
        _invested: hasBasis && stats.invested > 0 ? formatCurrencyFromUsd(stats.invested) : DEFAULT_VALUE,
        _profit: stats.profit == null || Number(stats.profit) === 0 ? DEFAULT_VALUE : formatProfit(stats.profit, stats.invested, stats.totalInvested),
        _share: share > 0 ? formatPercentage(share) : DEFAULT_VALUE,
        _buyOrders: formatUsdValueOrDash(stats.buyOrders),
        _sellOrders: stats.sellOrders > 0 ? `${formatQuantity(stats.sellOrders)}${symbol ? ' ' : ''}${symbol ?? ''}` : DEFAULT_VALUE,
      };
    });
  }, [assets, portfolio.costNow, displayCurrency]);

  const filteredAssets = useMemo(() => {
    let result = preparedAssets;
    if (hideCheap) {
      result = result.filter(asset => (asset.costNow || 0) >= 1 || !asset.hasTransactions);
    }
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
    createAssetNameColumn(openItem, 'portfolio_asset', portfolio.id, (record) => <AssetActionsDropdown portfolio={portfolio} asset={record} onUpdate={onRefresh} />),
{
      dataIndex: '_quantity',
      title: 'Количество',
      render: (value) => value,
      width: 200,
      sorter: (a, b) => a.quantity - b.quantity,
    },
    {
      dataIndex: '_avgPrice',
      title: 'Средняя цена',
      render: (value) => value,
      width: 200,
      sorter: (a, b) => a.averagePrice - b.averagePrice,
    },
    {
      dataIndex: '_cost',
      title: 'Стоимость',
      render: (value) => value,
      width: 200,
      sorter: (a, b) => a.costNow - b.costNow,
    },
    {
      dataIndex: '_invested',
      title: 'Вложено',
      render: (value) => value,
      width: 120,
      sorter: (a, b) => a.invested - b.invested,
    },
    {
      key: 'profit',
      title: 'Прибыль',
      render: (_, record) => {
        if (record._profit === DEFAULT_VALUE) return DEFAULT_VALUE;
        return <span className={getColorClass(record.profit)}>{record._profit}</span>;
      },
      width: 120,
      sorter: (a, b) => a.profit - b.profit,
    },
    {
      dataIndex: '_share',
      title: 'Доля',
      render: (value) => value,
      width: 120,
      sorter: (a, b) => a.share - b.share,
    },
    {
      dataIndex: '_buyOrders',
      title: 'Ордера на покупку',
      render: (value) => value,
      width: 120,
      sorter: (a, b) => (a.buyOrders || 0) - (b.buyOrders || 0),
    },
    {
      dataIndex: '_sellOrders',
      title: 'Ордера на продажу',
      render: (value) => value,
      width: 120,
      sorter: (a, b) => (a.sellOrders || 0) - (b.sellOrders || 0),
    },
  ], [openItem, portfolio, onRefresh]);

  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 16 }}>
        <Input
          placeholder="Поиск..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          allowClear
          variant="filled"
          style={{ width: 160 }}
        />
        <TagFilter onChange={setTagFilterIds} scope="asset" />
        <Checkbox checked={hideCheap} onChange={(e) => setHideCheap(e.target.checked)}>
          Спрятать дешевле {formatCurrency(1, 'USD')}
        </Checkbox>
        <Checkbox checked={showArchived} onChange={(e) => setShowArchived(e.target.checked)}>
          Показывать архивные
        </Checkbox>
      </div>

      {showingArchivedFallback && (
        <Alert
          title="Нет активных активов — показаны архивные"
          type="info"
          style={{ marginBottom: 16 }}
        />
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
