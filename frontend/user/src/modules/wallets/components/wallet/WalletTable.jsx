import React, { memo, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import TickerAvatar from 'src/components/TickerAvatar';
import { useNavigation } from 'src/hooks/useNavigation';
import { usePersistedState } from '@portfolio/shared';
import AssetActionsDropdown from '../AssetActionsDropdown';
import TagFilter from 'src/modules/tags/components/TagFilter';
import TagBadges from 'src/modules/tags/components/TagBadges';
import { Alert } from '@portfolio/shared';
import { Input, Checkbox } from 'antd';
import { formatCurrency, formatProfit, formatPercentage, getColorClass } from 'src/utils/format';

const DEFAULT_VALUE = '-';
const mutedStyle = { color: 'var(--text-muted)' };

const WalletTable = memo(({ wallet, assets, onRefresh }) => {
  const { openItem } = useNavigation();
  const [tagFilterIds, setTagFilterIds] = useState([]);
  const [search, setSearch] = useState('');
  const [hideCheap, setHideCheap] = usePersistedState('wallet-hide-cheap', false);
  const [showArchived, setShowArchived] = usePersistedState('wallet-archive', false);

  const preparedAssets = useMemo(() => {
    if (!assets) return [];

    return assets.map(asset => {
      const assetQuantity = Number(asset.quantity) || 0;
      const assetAmount = Number(asset.amount) || 0;
      const assetRealizedProfit = Number(asset.realizedProfit) || 0;
      const assetTotalInvested = Number(asset.totalInvested) || 0;
      const assetBuyOrders = Number(asset.buyOrders) || 0;
      const assetSellOrders = Number(asset.sellOrders) || 0;
      const assetAveragePrice = assetQuantity > 0 ? assetAmount / assetQuantity : 0;
      const share = wallet.costNow > 0 ? (asset.costNow / wallet.costNow) * 100 : 0;
      const symbol = asset.symbol?.toUpperCase();

      return {
        ...asset,
        share,
        symbol,
        averagePrice: assetAveragePrice,
        invested: Math.max(0, assetAmount),
        totalInvested: assetTotalInvested || Math.max(0, assetAmount),
        realizedProfit: assetRealizedProfit,
        buyOrders: assetBuyOrders,
        sellOrders: assetSellOrders,
        _quantity: assetQuantity > 0 ? `${assetQuantity}${symbol ? ' ' : ''}${symbol ?? ''}` : DEFAULT_VALUE,
        _avgPrice: formatCurrency(assetAveragePrice),
        _cost: formatCurrency(asset.costNow),
        _invested: formatCurrency(Math.max(0, assetAmount)),
        _profit: formatProfit(asset.profit ?? asset.costNow - assetAmount + assetRealizedProfit, Math.max(0, assetAmount), assetTotalInvested),
        _share: formatPercentage(share),
        _buyOrders: formatCurrency(assetBuyOrders || 0),
        _sellOrders: formatCurrency(assetSellOrders || 0),
        _hide: !assetQuantity,
      };
    });
  }, [assets, wallet.costNow]);

  const filteredAssets = useMemo(() => {
    let result = preparedAssets;
    if (hideCheap) {
      result = result.filter(asset => asset.costNow >= 1 || !asset.hasTransactions);
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
          <div style={{ display: 'flex', gap: 8, flex: 1 }} onClick={() => openItem(record, 'wallet_asset', wallet.id)}>
            <TickerAvatar src={record.image} symbol={record.symbol} size={24} style={{ cursor: 'pointer' }} />
            <div style={{ display: 'flex', flexDirection: 'column', cursor: 'pointer' }}>
              <span style={{ display: 'flex', alignItems: 'flex-start' }}>
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flexShrink: 1, minWidth: 0 }} title={record.name}>{record.name}</span>
                <span style={{ ...mutedStyle, textTransform: 'uppercase', marginLeft: 4, flexShrink: 0 }}>{record.symbol}</span>
                {record.isArchived && <span style={{ ...mutedStyle, fontSize: 10, whiteSpace: 'nowrap', flexShrink: 0, marginLeft: 4, marginTop: 1 }}>Архивный</span>}
              </span>
              <TagBadges tags={record.tags} entityType="wallet_asset" entityId={record.id} parentId={wallet.id} assignedTags={record.tags} />
            </div>
          </div>
          <div className="row-actions" onClick={e => e.stopPropagation()} style={{ flexShrink: 0, alignSelf: 'flex-start' }}>
            <AssetActionsDropdown wallet={wallet} asset={record} onUpdate={onRefresh} />
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
    {
      dataIndex: '_sellOrders',
      title: 'В ордерах на продажу',
      render: (value, record) => (record._hide && !record.sellOrders) ? DEFAULT_VALUE : value,
      width: 120,
      sorter: (a, b) => (a.sellOrders || 0) - (b.sellOrders || 0),
    },
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
