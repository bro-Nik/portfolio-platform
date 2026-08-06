import React, { memo, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import TickerAvatar from 'src/components/TickerAvatar';
import { useNavigation } from 'src/hooks/useNavigation';
import { usePersistedState } from '@portfolio/shared';
import AssetActionsDropdown from '../AssetActionsDropdown';
import TagFilter from 'src/modules/tags/components/TagFilter';
import TagBadges from 'src/modules/tags/components/TagBadges';
import { Alert } from '@portfolio/shared';
import { Checkbox, Input } from 'antd';
import { formatCurrency, formatProfit, formatPercentage, getColorClass } from 'src/utils/format';
import { calculatePortfolioAssetStats } from 'src/utils/assetStats';

const DEFAULT_VALUE = '-';
const mutedStyle = { color: 'var(--text-muted)' };

const PortfolioTable = memo(({ portfolio, assets, onRefresh }) => {
  const { openItem } = useNavigation();

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
        _quantity: assetQuantity > 0 ? `${assetQuantity}${symbol ? ' ' : ''}${symbol ?? ''}` : DEFAULT_VALUE,
        _avgPrice: stats.averagePrice == null ? DEFAULT_VALUE : formatCurrency(stats.averagePrice),
        _cost: stats.costNow == null ? DEFAULT_VALUE : formatCurrency(stats.costNow),
        _invested: hasBasis ? formatCurrency(stats.invested) : DEFAULT_VALUE,
        _profit: stats.profit == null ? DEFAULT_VALUE : formatProfit(stats.profit, stats.invested, stats.totalInvested),
        _share: formatPercentage(share),
        _buyOrders: formatCurrency(stats.buyOrders || 0),
        _hide: !assetQuantity,
      };
    });
  }, [assets, portfolio.costNow]);

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
    {
      key: 'name',
      title: 'Актив',
      fixed: 'left',
      render: (_, record) => (
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
          <div style={{ display: 'flex', gap: 8, flex: 1 }} onClick={() => openItem(record, 'portfolio_asset', portfolio.id)}>
            <TickerAvatar src={record.image} symbol={record.symbol} size={24} style={{ cursor: 'pointer' }} />
            <div style={{ display: 'flex', flexDirection: 'column', cursor: 'pointer' }}>
              <span style={{ display: 'flex', alignItems: 'flex-start' }}>
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flexShrink: 1, minWidth: 0 }} title={record.name}>{record.name}</span>
                <span style={{ ...mutedStyle, textTransform: 'uppercase', marginLeft: 4, flexShrink: 0 }}>{record.symbol}</span>
                {record.isArchived && <span style={{ ...mutedStyle, fontSize: 10, whiteSpace: 'nowrap', flexShrink: 0, marginLeft: 4, marginTop: 1 }}>Архивный</span>}
              </span>
              <TagBadges tags={record.tags} entityType="portfolio_asset" entityId={record.id} parentId={portfolio.id} assignedTags={record.tags} />
            </div>
          </div>
          <div className="row-actions" onClick={e => e.stopPropagation()} style={{ flexShrink: 0, alignSelf: 'flex-start' }}>
            <AssetActionsDropdown portfolio={portfolio} asset={record} onUpdate={onRefresh} />
          </div>
        </div>
      ),
      maxWidth: 300,
      sorter: (a, b) => (a.name || '').localeCompare(b.name || ''),
    },
    {
      dataIndex: '_quantity',
      title: 'Количество',
      render: (value, record) => record._hide ? DEFAULT_VALUE : value,
      width: 200,
      sorter: (a, b) => a.quantity - b.quantity,
    },
    {
      dataIndex: '_avgPrice',
      title: 'Средняя цена',
      render: (value, record) => record._hide ? DEFAULT_VALUE : value,
      width: 200,
      sorter: (a, b) => a.averagePrice - b.averagePrice,
    },
    {
      dataIndex: '_cost',
      title: 'Стоимость',
      render: (value, record) => record._hide ? DEFAULT_VALUE : value,
      width: 200,
      sorter: (a, b) => a.costNow - b.costNow,
    },
    {
      dataIndex: '_invested',
      title: 'Вложено',
      render: (value, record) => record._hide ? DEFAULT_VALUE : value,
      width: 120,
      sorter: (a, b) => a.invested - b.invested,
    },
    {
      key: 'profit',
      title: 'Прибыль',
      render: (_, record) => {
        if (record._hide) return DEFAULT_VALUE;
        return <span className={getColorClass(record.profit)}>{record._profit}</span>;
      },
      width: 120,
      sorter: (a, b) => a.profit - b.profit,
    },
    {
      dataIndex: '_share',
      title: 'Доля',
      render: (value, record) => record._hide ? DEFAULT_VALUE : value,
      width: 120,
      sorter: (a, b) => a.share - b.share,
    },
    {
      dataIndex: '_buyOrders',
      title: 'В ордерах на покупку',
      render: (value, record) => (record._hide && !record.buyOrders) ? DEFAULT_VALUE : value,
      width: 120,
      sorter: (a, b) => (a.buyOrders || 0) - (b.buyOrders || 0),
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
          Спрятать дешевле $1
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
