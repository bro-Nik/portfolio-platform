import React, { memo } from 'react';
import { useTable } from '/app/src/hooks/useTable';
import { Table } from './Table';
import EmptyState from '/app/src/components/EmptyState';

const DataTable = memo(({ 
  data, 
  columnsConfig, 
  fallbackData = [], 
  placeholder = "Поиск...",
  storageKey,
  children 
}) => {
  const { table, globalFilter, setGlobalFilter } = useTable(data, columnsConfig, fallbackData, storageKey);

  if (!data || !data.length) return <EmptyState />

  return (
    <Table 
      table={table}
      globalFilter={globalFilter}
      setGlobalFilter={setGlobalFilter}
      placeholder={placeholder}
    >
      {children}
    </Table>
  );
});

export default DataTable;
