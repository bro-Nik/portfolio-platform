import React, { memo, useState } from 'react';
import { Table, Input } from 'antd';
import { useLocalStorage } from 'src/hooks/useLocalStorage';
import EmptyState from 'src/components/EmptyState';

const DataTable = memo(({
  data,
  columnsConfig,
  fallbackData = [],
  placeholder = "Поиск...",
  storageKey,
  children
}) => {
  const sourceData = data ?? fallbackData;
  const [sortState, setSortState] = useLocalStorage(storageKey || '', null);
  const [globalFilter, setGlobalFilter] = useState('');

  if (!sourceData.length) return <EmptyState />;

  const filteredData = globalFilter
    ? sourceData.filter(record =>
        Object.values(record).some(val =>
          val != null && String(val).toLowerCase().includes(globalFilter.toLowerCase())
        )
      )
    : sourceData;

  const columns = columnsConfig.map(col => {
    const isSorted = sortState && sortState.field === col.dataIndex;
    return {
      ...col,
      sortOrder: isSorted ? sortState.order : undefined,
    };
  });

  const handleTableChange = (_pagination, _filters, sorter) => {
    const singleSorter = Array.isArray(sorter) ? sorter[0] : sorter;
    if (!singleSorter || !singleSorter.field) {
      setSortState(null);
    } else {
      setSortState({
        field: singleSorter.field,
        order: singleSorter.order,
      });
    }
  };

  return (
    <div className="table-wrapper">
      <div className="table-controls" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: '0 0 50%', maxWidth: '50%' }}>
            <Input
              placeholder={placeholder}
              value={globalFilter ?? ''}
              onChange={(e) => setGlobalFilter(e.target.value)}
              allowClear
            />
          </div>
          {children}
        </div>
      </div>

      <Table
        dataSource={filteredData}
        columns={columns}
        onChange={handleTableChange}
        pagination={false}
        rowKey={(record) => record.id ?? record.key ?? Math.random()}
        size="small"
        showSorterTooltip={false}
        scroll={{ x: 'max-content' }}
      />
    </div>
  );
});

export default DataTable;
