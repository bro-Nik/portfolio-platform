import React, { memo, useMemo } from 'react';
import DataTable from '/app/src/features/tables/DataTable';
import { useNavigation } from '/app/src/hooks/useNavigation';
import { useTicker } from '/app/src/hooks/useTicker';
import { useLocalStorage } from '/app/src/hooks/useLocalStorage';
import AssetActionsDropdown from '../AssetActionsDropdown';
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
} from '/app/src/features/tables/tableColumns';

const PortfolioTable = memo(({ portfolio, assets }) => {
  const { openItem } = useNavigation();
  const { getTicker } = useTicker();

  const [hideCheap, setHideCheap] = useLocalStorage('portfolio-hide-cheap', false);

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
    if (!hideCheap) return preparedAssets;
    return preparedAssets.filter(asset => asset.costNow >= 1);
  }, [preparedAssets, hideCheap]);

  const columns = useMemo(() => [
    createAssetNameColumn(openItem, 'portfolio_asset', portfolio.id),
    createQuantityColumn((a) => a.symbol, (a) => !a.quantity),
    createAveragePriceColumn((a) => !a.averagePrice),
    createCostColumn((a) => !a.quantity),
    createInvestedColumn((a) => !a.quantity),
    createProfitColumn((a) => !a.quantity),
    createShareColumn((a) => !a.quantity),
    createBuyOrdersColumn((a) => !a.quantity && !a.buyOrders),
    createActionsColumn(({ row }) => <AssetActionsDropdown portfolio={portfolio} asset={row.original} btn='icon' />),
  ], [openItem, portfolio]);

  return (
    <>
      <div className="d-flex align-items-center gap-3 flex-wrap mb-1">
        <label className="text-nowrap small mb-0 d-flex align-items-center gap-1 cursor-pointer">
          <input
            type="checkbox"
            className="form-check-input mt-0"
            checked={hideCheap}
            onChange={(e) => setHideCheap(e.target.checked)}
          />
          Спрятать дешевле $1
        </label>
      </div>

    <DataTable 
      data={filteredAssets}
      columnsConfig={columns}
      placeholder="Поиск по активам..."
    >
      <div className="d-flex align-items-center gap-3 flex-wrap mt-1">
        {portfolio.comment && (
          <span className="text-muted small">{portfolio.comment}</span>
        )}
      </div>
    </DataTable>
    </>
  );
});

export default PortfolioTable;
