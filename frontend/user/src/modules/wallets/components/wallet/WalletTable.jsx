import React, { memo, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { useNavigation } from 'src/hooks/useNavigation';
import { usePersistedState } from '@portfolio/shared';
import AssetActionsDropdown from '../AssetActionsDropdown';
import TagFilter from 'src/modules/tags/components/TagFilter';
import { Alert } from '@portfolio/shared';
import { Input, Checkbox } from 'antd';
import { formatCurrency, formatPercentage, formatQuantity, formatUsdValueOrDash } from 'src/utils/format';
import { useDisplayCurrency } from 'src/utils/currency';
import { createAssetNameColumn } from 'src/features/tables/tableColumns';

const DEFAULT_VALUE = '-';

const WalletTable = memo(({ wallet, assets, onRefresh }) => {
  const { openItem } = useNavigation();
  const displayCurrency = useDisplayCurrency();
  const [tagFilterIds, setTagFilterIds] = useState([]);
  const [search, setSearch] = useState('');
  const [hideCheap, setHideCheap] = usePersistedState('wallet-hide-cheap', false);
  const [showArchived, setShowArchived] = usePersistedState('wallet-archive', false);

  const preparedAssets = useMemo(() => {
    if (!assets) return [];

    return assets.map(asset => {
      const assetQuantity = Number(asset.quantity) || 0;
      const assetBuyOrders = Number(asset.buyOrders) || 0;
      const assetSellOrders = Number(asset.sellOrders) || 0;
      const share = wallet.costNow > 0 ? (asset.costNow / wallet.costNow) * 100 : 0;
      const symbol = asset.symbol?.toUpperCase();

      return {
        ...asset,
        share,
        symbol,
        buyOrders: assetBuyOrders,
        sellOrders: assetSellOrders,
        _quantity: assetQuantity > 0 ? `${formatQuantity(assetQuantity)}${symbol ? ' ' : ''}${symbol ?? ''}` : DEFAULT_VALUE,
        _cost: formatUsdValueOrDash(asset.costNow),
        _share: share > 0 ? formatPercentage(share) : DEFAULT_VALUE,
        _buyOrders: formatUsdValueOrDash(assetBuyOrders),
        _sellOrders: assetSellOrders > 0 ? `${formatQuantity(assetSellOrders)}${symbol ? ' ' : ''}${symbol ?? ''}` : DEFAULT_VALUE,
      };
    });
  }, [assets, wallet.costNow, displayCurrency]);

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
    createAssetNameColumn(openItem, 'wallet_asset', wallet.id, (record) => <AssetActionsDropdown wallet={wallet} asset={record} onUpdate={onRefresh} />),
    {
      dataIndex: '_quantity',
      title: 'Количество',
      render: (value) => value,
      width: 200,
      sorter: (a, b) => a.quantity - b.quantity,
    },
    {
      dataIndex: '_cost',
      title: 'Стоимость',
      render: (value) => value,
      width: 200,
      sorter: (a, b) => a.costNow - b.costNow,
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
  ], [openItem, wallet, onRefresh]);

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
        storageKey="wallet-table-sorting"
        rowClassName={(record) => record.isArchived ? 'archived-row' : ''}
      />
    </>
  );
});

export default WalletTable;
