import React, { memo, useCallback, useMemo, useState } from 'react';
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
import TagFilter from '../TagFilter';
import { portfolioApi } from '../../api/portfolioApi';
import { useDataStore } from '/app/src/stores/dataStore';

const PortfoliosTable = memo(({ portfolios }) => {
  const { openItem } = useNavigation();
  const setPortfolios = useDataStore(state => state.setPortfolios);
  const [tagFilterIds, setTagFilterIds] = useState([]);

  const handleRefresh = useCallback(async () => {
    const result = await portfolioApi.getPortfolios();
    if (result.success) setPortfolios(result.data.portfolios || []);
  }, [setPortfolios]);

  const filtered = useMemo(() => {
    if (tagFilterIds.length === 0) return portfolios;
    return portfolios.filter(p =>
      p.tags?.some(t => tagFilterIds.includes(t.id))
    );
  }, [portfolios, tagFilterIds]);

  const columns = useMemo(() => [
    createNameColumn(openItem, 'portfolio'),
    createCostColumn(),
    createInvestedColumn(),
    createProfitColumn(),
    createShareColumn(),
    createBuyOrdersColumn(),
    createActionsColumn(({ row }) => <PortfolioActionsDropdown portfolio={row.original} btn='icon' onUpdate={handleRefresh} />),
  ], [openItem, handleRefresh]);

  return (
    <>
      <div className="mb-1">
        <TagFilter onChange={setTagFilterIds} />
      </div>
      <DataTable 
        data={filtered}
        columnsConfig={columns}
        placeholder="Поиск по портфелям..."
        storageKey="portfolios-list-sorting"
      />
    </>
  );
});

export default PortfoliosTable;
