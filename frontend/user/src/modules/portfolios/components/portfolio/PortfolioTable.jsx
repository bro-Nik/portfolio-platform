import React, { memo, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { useNavigation } from 'src/hooks/useNavigation';
import { useTicker } from 'src/hooks/useTicker';
import { useLocalStorage } from 'src/hooks/useLocalStorage';
import AssetActionsDropdown from '../AssetActionsDropdown';
import TagFilter from '../TagFilter';
import { Checkbox } from 'antd';
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
  const { getTicker } = useTicker();

  const [hideCheap, setHideCheap] = useLocalStorage('portfolio-hide-cheap', false);
  const [tagFilterIds, setTagFilterIds] = useState([]);

  // Подготавливаем данные для таблицы
  const preparedAssets = useMemo(() => {
    if (!assets) return [];

    return assets.map(asset => {
      const ticker = getTicker(asset.tickerId);

      return {
        ...asset,
        share: portfolio.costNow > 0 ? (asset.costNow / portfolio.costNow) * 100 : 0,
        image: ticker?.image,
        name: ticker?.name,
        symbol: ticker?.symbol,
      };
    });
  }, [assets, portfolio.costNow]);

  const filteredAssets = useMemo(() => {
    let result = preparedAssets;
    if (hideCheap) result = result.filter(asset => asset.costNow >= 1);
    if (tagFilterIds.length > 0) {
      result = result.filter(asset =>
        asset.tags?.some(t => tagFilterIds.includes(t.id))
      );
    }
    return result;
  }, [preparedAssets, hideCheap, tagFilterIds]);

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
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 4 }}>
        <Checkbox checked={hideCheap} onChange={(e) => setHideCheap(e.target.checked)}>
          Спрятать дешевле $1
        </Checkbox>
        <TagFilter onChange={setTagFilterIds} />
      </div>

    <DataTable 
      data={filteredAssets}
      columnsConfig={columns}
      placeholder="Поиск по активам..."
      storageKey="portfolio-table-sorting"
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginTop: 4 }}>
        {portfolio.comment && (
          <span style={{ color: 'rgba(0,0,0,0.45)', fontSize: '12px' }}>{portfolio.comment}</span>
        )}
      </div>
    </DataTable>
    </>
  );
});

export default PortfolioTable;
