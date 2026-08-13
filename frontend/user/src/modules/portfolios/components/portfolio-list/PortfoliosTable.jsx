import React, { memo, useCallback, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { useNavigation } from 'src/hooks/useNavigation';
import { Alert } from '@portfolio/shared';
import { Checkbox, Input } from 'antd';
import {
  createCostColumn,
  createShareColumn,
  createBuyOrdersColumn,
  createProfitColumn,
  createInvestedColumn,
  createNameColumn
} from 'src/features/tables/tableColumns';
import PortfolioActionsDropdown from '../PortfolioActionsDropdown'
import TagFilter from 'src/modules/tags/components/TagFilter';
import { useQueryClient } from '@tanstack/react-query';
import { useDisplayCurrency } from 'src/utils/currency';
import { usePortfolioMutations } from '../../hooks/usePortfolioMutations';

const PortfoliosTable = memo(({ portfolios, showArchived, onToggleArchived, showingArchivedFallback }) => {
  const { openItem } = useNavigation();
  const queryClient = useQueryClient();
  const displayCurrency = useDisplayCurrency();
  const { editPortfolio } = usePortfolioMutations();
  const [tagFilterIds, setTagFilterIds] = useState([]);
  const [search, setSearch] = useState('');

  const handleRefresh = useCallback(async () => {
    queryClient.invalidateQueries({ queryKey: ['overview'] });
  }, [queryClient]);

  const handleEditComment = useCallback(async (record, comment) => {
    await editPortfolio.mutateAsync({ id: record.id, name: record.name, market: record.market, comment });
  }, [editPortfolio]);

  const filtered = useMemo(() => {
    let result = portfolios;
    if (tagFilterIds.length > 0) {
      result = result.filter(p =>
        p.tags?.some(t => tagFilterIds.includes(t.id))
      );
    }
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(p =>
        p.name && p.name.toLowerCase().includes(q)
      );
    }
    return result;
  }, [portfolios, tagFilterIds, search]);

  const columns = useMemo(() => [
    createNameColumn(openItem, 'portfolio', (record) => <PortfolioActionsDropdown portfolio={record} onUpdate={handleRefresh} />, handleEditComment),
    createCostColumn(),
    createInvestedColumn(),
    createProfitColumn(),
    createShareColumn(),
    createBuyOrdersColumn(),
  ], [openItem, handleRefresh, handleEditComment, displayCurrency]);

  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <Input
          placeholder="Поиск..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          allowClear
          variant="filled"
          style={{ width: 160 }}
        />
        <TagFilter onChange={setTagFilterIds} scope="portfolio" />
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Checkbox checked={showArchived} onChange={(e) => onToggleArchived(e.target.checked)}>
            Показывать архивные
          </Checkbox>
        </div>
      </div>
      {showingArchivedFallback && (
        <Alert
          title="Нет активных портфелей — показаны архивные"
          type="info"
          style={{ marginBottom: 16 }}
        />
      )}
      <DataTable
        data={filtered}
        columnsConfig={columns}
        storageKey="portfolios-list-sorting"
        rowClassName={(record) => record.isArchived ? 'archived-row' : ''}
      />
    </>
  );
});

export default PortfoliosTable;
