import React, { memo, useMemo } from 'react';
import DataTable from '/app/src/features/tables/DataTable';
import { useNavigation } from '/app/src/hooks/useNavigation';
import { createCostColumn, createShareColumn, createBuyOrdersColumn, createNameColumn, createActionsColumn } from '/app/src/features/tables/tableColumns';
import WalletActionsDropdown from '../WalletActionsDropdown'

const WalletsTable = memo(({ wallets }) => {
  const { openItem } = useNavigation();

  const columns = useMemo(() => [
    createNameColumn(openItem, 'wallet'),
    createCostColumn(),
    createShareColumn(),
    createBuyOrdersColumn(),
    createActionsColumn(({ row }) => <WalletActionsDropdown wallet={row.original} btn='icon' />),
  ], [openItem]);

  return (
    <DataTable 
      data={wallets}
      columnsConfig={columns}
      placeholder="Поиск по кошелькам..."
    />
  );
});

export default WalletsTable;
