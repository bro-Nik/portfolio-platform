import React, { memo, useCallback, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { useNavigation } from 'src/hooks/useNavigation';
import { Alert, Checkbox, Input } from 'antd';
import { createCostColumn, createShareColumn, createBuyOrdersColumn, createNameColumn, createActionsColumn } from 'src/features/tables/tableColumns';
import WalletActionsDropdown from '../WalletActionsDropdown'
import TagFilter from 'src/modules/portfolios/components/TagFilter';
import { useQueryClient } from '@tanstack/react-query';

const WalletsTable = memo(({ wallets, showArchived, onToggleArchived, showingArchivedFallback }) => {
  const { openItem } = useNavigation();
  const queryClient = useQueryClient();
  const [tagFilterIds, setTagFilterIds] = useState([]);
  const [search, setSearch] = useState('');

  const handleRefresh = useCallback(async () => {
    queryClient.invalidateQueries({ queryKey: ['wallets'] });
  }, [queryClient]);

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
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Checkbox checked={showArchived} onChange={(e) => onToggleArchived(e.target.checked)}>
            Показывать архивные
          </Checkbox>
        </div>
      </div>
      {showingArchivedFallback && (
        <Alert
          message="Нет активных кошельков — показаны архивные"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      <DataTable
        data={filtered}
        columnsConfig={columns}
        storageKey="wallets-list-sorting"
        rowClassName={(record) => record.isArchived ? 'archived-row' : ''}
      />
    </>
  );
});

export default WalletsTable;
