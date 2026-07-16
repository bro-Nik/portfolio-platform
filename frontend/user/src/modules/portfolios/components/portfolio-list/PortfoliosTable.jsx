import React, { memo, useCallback, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { useNavigation } from 'src/hooks/useNavigation';
import {
  createCostColumn,
  createShareColumn,
  createBuyOrdersColumn,
  createActionsColumn,
  createProfitColumn,
  createInvestedColumn,
  createNameColumn
} from 'src/features/tables/tableColumns';
import PortfolioActionsDropdown from '../PortfolioActionsDropdown'
import TagFilter from '../TagFilter';
import { portfolioApi } from '../../api/portfolioApi';
import { useDataStore } from 'src/stores/dataStore';

const PortfoliosTable = memo(({ portfolios }) => {
  const { openItem } = useNavigation();
  const setPortfolios = useDataStore(state => state.setPortfolios);
  const [tagFilterIds, setTagFilterIds] = useState([]);

  const handleRefresh = useCallback(async () => {
    try {
      const data = await portfolioApi.getPortfolios();
      setPortfolios(data.portfolios || []);
    } catch (error) {
      console.warn('Ошибка обновления портфелей:', error);
    }
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
      <div style={{ marginBottom: 4 }}>
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
