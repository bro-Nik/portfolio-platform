import React, { memo, useCallback, useMemo, useState } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { Alert } from '@portfolio/shared';
import { Checkbox, Input, Tag } from 'antd';
import TickerAvatar from 'src/components/TickerAvatar';
import CommentCell from 'src/features/forms/CommentCell';
import { useNavigation } from 'src/hooks/useNavigation';
import { formatCurrencyFromUsd } from 'src/utils/format';
import { useDisplayCurrency } from 'src/utils/currency';
import { useWatchlistOperations } from '../hooks/useWatchlistOperations';
import { isTriggered } from '../utils/alerts';
import WatchlistAssetActionsDropdown from './WishlistAssetActionsDropdown';

const mutedStyle = { color: 'var(--text-muted)' };
const smallTextStyle = { fontSize: '12px' };

const WatchlistTable = memo(({ items, showArchived, onToggleArchived, showingArchivedFallback }) => {
  const { openItem } = useNavigation();
  const { editItemComment } = useWatchlistOperations();
  useDisplayCurrency();
  const [search, setSearch] = useState('');

  const handleEditComment = useCallback(async (record, comment) => {
    await editItemComment(record.id, comment);
  }, [editItemComment]);

  const filtered = useMemo(() => {
    if (!search) return items;
    const q = search.toLowerCase();
    return items.filter(i =>
      (i.name && i.name.toLowerCase().includes(q)) ||
      (i.symbol && i.symbol.toLowerCase().includes(q))
    );
  }, [items, search]);

  const columns = useMemo(() => [
    {
      dataIndex: 'name',
      title: 'Актив',
      fixed: 'left',
      render: (_, record) => (
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
          <div style={{ display: 'flex', gap: 8, flex: 1 }}>
            <TickerAvatar src={record.image} symbol={record.symbol} size={24} />
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ display: 'flex', alignItems: 'flex-start', cursor: 'pointer' }} onClick={() => openItem({ ...record, name: record.symbol || record.name }, 'wishlist_item')}>
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flexShrink: 1, minWidth: 0 }} title={record.name}>
                  {record.name || record.symbol}
                </span>
                <span style={{ ...mutedStyle, textTransform: 'uppercase', marginLeft: 4, flexShrink: 0 }}>{record.symbol}</span>
                {record.isArchived && <span style={{ ...mutedStyle, fontSize: 10, whiteSpace: 'nowrap', flexShrink: 0, marginLeft: 4, marginTop: 1 }}>Архивный</span>}
              </span>
              <span style={{ ...mutedStyle, ...smallTextStyle, textTransform: 'capitalize' }}>{record.market}</span>
              <span style={{ display: 'flex', alignItems: 'center', ...mutedStyle, ...smallTextStyle, gap: 8 }}>
                {(record.alerts?.length || 0)} уведомлений
                <CommentCell comment={record.comment} onSave={(comment) => handleEditComment(record, comment)} />
              </span>
            </div>
          </div>
          <div className="row-actions" onClick={e => e.stopPropagation()} style={{ flexShrink: 0, alignSelf: 'flex-start' }}>
            <WatchlistAssetActionsDropdown item={record} />
          </div>
        </div>
      ),
      maxWidth: 300,
      sorter: (a, b) => (a.name || a.symbol || '').localeCompare(b.name || b.symbol || ''),
    },
    {
      dataIndex: 'price',
      title: 'Цена',
      render: (value) => formatCurrencyFromUsd(value),
      width: 160,
      sorter: (a, b) => (a.price ?? 0) - (b.price ?? 0),
    },
    {
      key: 'alerts',
      title: 'Уведомления',
      render: (_, record) => {
        const alerts = record.alerts || [];
        const active = alerts.filter(a => a.isActive && !a.isArchived);
        const triggered = alerts.filter(isTriggered);
        return (
          <span style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            {triggered.length > 0 && <Tag color="success">{triggered.length} сработал</Tag>}
            {active.length > 0 && <Tag color="processing">{active.length} активн.</Tag>}
            {alerts.length === 0 && <span style={{ ...mutedStyle, ...smallTextStyle }}>нет</span>}
          </span>
        );
      },
      width: 200,
    },
  ], [handleEditComment, openItem]);

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
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Checkbox checked={showArchived} onChange={(e) => onToggleArchived(e.target.checked)}>
            Показывать архивные
          </Checkbox>
        </div>
      </div>
      {showingArchivedFallback && (
        <Alert
          title="Нет активных записей — показаны архивные"
          type="info"
          style={{ marginBottom: 16 }}
        />
      )}
      <DataTable
        data={filtered}
        columnsConfig={columns}
        storageKey="watchlist-sorting"
        rowClassName={(record) => record.isArchived ? 'archived-row' : ''}
      />
    </>
  );
});

export default WatchlistTable;
