import React, { memo, useCallback, useMemo, useState } from 'react';
import DataTable from '/app/src/features/tables/DataTable';
import { useNavigation } from '/app/src/hooks/useNavigation';
import { createCostColumn, createShareColumn, createBuyOrdersColumn, createNameColumn, createActionsColumn } from '/app/src/features/tables/tableColumns';
import WalletActionsDropdown from '../WalletActionsDropdown'
import TagFilter from '/app/src/modules/portfolios/components/TagFilter';
import { walletApi } from '../../api/walletApi';
import { useDataStore } from '/app/src/stores/dataStore';

const WalletsTable = memo(({ wallets }) => {
  const { openItem } = useNavigation();
  const setWallets = useDataStore(state => state.setWallets);
  const [tagFilterIds, setTagFilterIds] = useState([]);

  const handleRefresh = useCallback(async () => {
    const result = await walletApi.getAllWallets();
    if (result.success) setWallets(result.data.wallets || []);
  }, [setWallets]);

  const filtered = useMemo(() => {
    if (tagFilterIds.length === 0) return wallets;
    return wallets.filter(w =>
      w.tags?.some(t => tagFilterIds.includes(t.id))
    );
  }, [wallets, tagFilterIds]);

  const columns = useMemo(() => [
    createNameColumn(openItem, 'wallet'),
    createCostColumn(),
    createShareColumn(),
    createBuyOrdersColumn(),
    createActionsColumn(({ row }) => <WalletActionsDropdown wallet={row.original} btn='icon' onUpdate={handleRefresh} />),
  ], [openItem, handleRefresh]);

  return (
    <>
      <div style={{ marginBottom: 4 }}>
        <TagFilter onChange={setTagFilterIds} />
      </div>
      <DataTable 
        data={filtered}
        columnsConfig={columns}
        placeholder="Поиск по кошелькам..."
        storageKey="wallets-list-sorting"
      />
    </>
  );
});

export default WalletsTable;
