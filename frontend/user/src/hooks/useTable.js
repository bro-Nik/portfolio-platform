import { useState } from 'react';
import { useReactTable, getCoreRowModel, getSortedRowModel, getFilteredRowModel } from '@tanstack/react-table';
import { useLocalStorage } from './useLocalStorage';

export const useTable = (data, columns, fallbackData = [], storageKey) => {
  const [sorting, setSorting] = useLocalStorage(storageKey || '', []);
  const [globalFilter, setGlobalFilter] = useState('');

  const table = useReactTable({
    data: data ?? fallbackData,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return {
    table,
    globalFilter,
    setGlobalFilter,
  };
};
