import React, { memo, useMemo } from 'react';
import DataTable from '/app/src/features/tables/DataTable';
import { useNavigation } from '/app/src/hooks/useNavigation';
import {
  createCostColumn,
  createShareColumn,
  createBuyOrdersColumn,
  createActionsColumn,
  createProfitColumn,
  createInvestedColumn,
  createNameColumn
} from '/app/src/features/tables/tableColumns';
import PortfolioActionsDropdown from '../PortfolioActionsDropdown'

const PortfoliosTable = memo(({ portfolios }) => {
  const { openItem } = useNavigation();

  const columns = useMemo(() => [
    createNameColumn(openItem, 'portfolio'),
    createCostColumn(),
    createInvestedColumn(),
    createProfitColumn(),
    createShareColumn(),
    createBuyOrdersColumn(),
    createActionsColumn(({ row }) => <PortfolioActionsDropdown portfolio={row.original} btn='icon' />),
  ], [openItem]);

  return (
    <DataTable 
      data={portfolios}
      columnsConfig={columns}
      placeholder="Поиск по портфелям..."
    />
  );
});

export default PortfoliosTable;
