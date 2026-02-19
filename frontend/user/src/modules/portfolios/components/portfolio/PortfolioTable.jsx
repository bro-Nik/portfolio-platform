import React, { memo, useMemo } from 'react';
import DataTable from '/app/src/features/tables/DataTable';
import { useNavigation } from '/app/src/hooks/useNavigation';
import { useTicker } from '/app/src/hooks/useTicker';
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
    <DataTable 
      data={preparedAssets}
      columnsConfig={columns}
      placeholder="Поиск по активам..."
      children={portfolio.comment}
    />
  );
});

export default PortfolioTable;
