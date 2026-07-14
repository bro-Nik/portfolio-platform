import React from 'react';
import { flexRender } from '@tanstack/react-table';
import { Input } from 'antd';

export const Table = ({ 
  table, 
  globalFilter, 
  setGlobalFilter, 
  placeholder = "Поиск...",
  children 
}) => {
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

      <div className="big-table">
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th
                    key={header.id}
                    style={{ width: header.getSize(), borderBottom: '2px solid #f0f0f0', padding: '8px 12px', textAlign: 'left', fontWeight: 600, fontSize: '14px' }}
                  >
                    {header.isPlaceholder ? null : (
                      <div
                        {...{
                          className: header.column.getCanSort() 
                            ? 'cursor-pointer select-none' 
                            : '',
                          onClick: header.column.getToggleSortingHandler(),
                        }}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                        {{
                          asc: ' 🔼',
                          desc: ' 🔽',
                        }[header.column.getIsSorted()] ?? null}
                      </div>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>

          <tbody>
            {table.getRowModel().rows.map(row => (
              <tr key={row.id}>
                {row.getVisibleCells().map(cell => (
                  <td
                    key={cell.id}
                    style={{ width: cell.column.getSize(), borderBottom: '1px solid #f0f0f0', padding: '8px 12px' }}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
