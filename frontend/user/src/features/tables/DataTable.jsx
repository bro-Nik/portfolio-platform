import React, { memo } from 'react';
import Table from 'src/components/Table';
import { usePersistedState } from '@portfolio/shared';

const DataTable = memo(({
  data,
  fallbackData,
  columnsConfig,
  storageKey,
  rowClassName,
}) => {
  const sourceData = data ?? fallbackData;
  const [sortState, setSortState] = usePersistedState(storageKey, null);

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
      <Table
        dataSource={sourceData}
        columns={columns}
        onChange={handleTableChange}
        pagination={false}
        rowKey={(record) => record.id ?? record.key ?? Math.random()}
        scroll={{ x: 'max-content' }}
        rowClassName={rowClassName}
      />
    </div>
  );
});

export default DataTable;
