import React, { memo, useCallback, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { useNavigation } from 'src/hooks/useNavigation';
import { Input } from 'antd';
import { createCostColumn, createShareColumn, createBuyOrdersColumn, createNameColumn, createActionsColumn } from 'src/features/tables/tableColumns';
import WalletActionsDropdown from '../WalletActionsDropdown'
import TagFilter from 'src/modules/portfolios/components/TagFilter';
import { walletApi } from '../../api/walletApi';
import { useDataStore } from 'src/stores/dataStore';

const WalletsTable = memo(({ wallets }) => {
  const { openItem } = useNavigation();
  const setWallets = useDataStore(state => state.setWallets);
  const [tagFilterIds, setTagFilterIds] = useState([]);
  const [search, setSearch] = useState('');

  const handleRefresh = useCallback(async () => {
    try {
      const data = await walletApi.getAllWallets();
      setWallets(data.wallets || []);
    } catch (error) {
      console.warn('Ошибка обновления кошельков:', error);
    }
  }, [setWallets]);

  const filtered = useMemo(() => {
    let result = wallets;
    if (tagFilterIds.length > 0) {
      result = result.filter(w =>
        w.tags?.some(t => tagFilterIds.includes(t.id))
      );
    }
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(w =>
        w.name && w.name.toLowerCase().includes(q)
      );
    }
    return result;
  }, [wallets, tagFilterIds, search]);

  const columns = useMemo(() => [
    createNameColumn(openItem, 'wallet'),
    createCostColumn(),
    createShareColumn(),
    createBuyOrdersColumn(),
    createActionsColumn(({ row }) => <WalletActionsDropdown wallet={row.original} btn='icon' onUpdate={handleRefresh} />),
  ], [openItem, handleRefresh]);

  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <Input
          placeholder="Поиск..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          allowClear
          style={{ width: 160 }}
        />
        <TagFilter onChange={setTagFilterIds} />
      </div>
      <DataTable
        data={filtered}
        columnsConfig={columns}
        storageKey="wallets-list-sorting"
      />
    </>
  );
});

export default WalletsTable;
