import { Table as AntTable, type TableProps } from 'antd';

const Table = <T extends object>(props: TableProps<T>) => (
  <AntTable<T> showSorterTooltip={false} {...props} />
);

export default Table;
