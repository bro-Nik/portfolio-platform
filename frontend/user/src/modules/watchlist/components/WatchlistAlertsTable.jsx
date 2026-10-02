import React, { memo, useCallback, useMemo } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { Tag } from 'antd';
import { ArrowDownRight, ArrowUpRight } from 'lucide-react';
import CommentCell from 'src/features/forms/CommentCell';
import { useModalStore } from '@portfolio/shared';
import { formatCurrencyFromUsd, formatDateTime } from 'src/utils/format';
import { useDisplayCurrency } from 'src/utils/currency';
import { useWatchlistOperations } from '../hooks/useWatchlistOperations';
import { DIRECTION_LABELS, distanceToTarget, isTriggered } from '../utils/alerts';
import AlertActionsDropdown from './AlertActionsDropdown';
import AlertEditModal from './modals/AlertEdit';

const mutedStyle = { color: 'var(--text-muted)' };
const smallTextStyle = { fontSize: '12px' };

const WatchlistAlertsTable = memo(({ item }) => {
  useDisplayCurrency();
  const { openModal } = useModalStore();
  const { saveAlert } = useWatchlistOperations();
  const alerts = useMemo(() => item.alerts || [], [item.alerts]);

  const handleEditComment = useCallback(async (record, comment) => {
    await saveAlert(item.id, record, { comment });
  }, [saveAlert, item.id]);

  const handleAlertClick = useCallback((alert) => {
    if (isTriggered(alert) || typeof alert.id !== 'number') return;
    openModal(AlertEditModal, { item, alert });
  }, [openModal, item]);

  const columns = useMemo(() => [
    {
      key: 'condition',
      title: 'Условие',
      fixed: 'left',
      render: (_, record) => {
        const triggered = isTriggered(record);
        const editable = !triggered && typeof record.id === 'number';
        const distance = !triggered && record.isActive
          ? distanceToTarget(item.price, record.targetPriceUsd, record.direction)
          : null;
        return (
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1 }}>
              <span
                style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: editable ? 'pointer' : 'default' }}
                onClick={() => { if (editable) handleAlertClick(record); }}
              >
                {record.direction === 'above'
                  ? <ArrowUpRight size={14} className="text-green" />
                  : <ArrowDownRight size={14} className="text-red" />}
                <span>{DIRECTION_LABELS[record.direction]} {formatCurrencyFromUsd(Number(record.targetPriceUsd))}</span>
              </span>
              <span style={{ display: 'flex', alignItems: 'center', ...mutedStyle, ...smallTextStyle, gap: 8 }}>
                {triggered ? (
                  <Tag color="success">Сработал {formatDateTime(record.triggeredAt)}</Tag>
                ) : !record.isActive ? (
                  <Tag>Выключен</Tag>
                ) : distance != null && distance > 0 ? (
                  <span>осталось {(distance * 100).toFixed(1)}%</span>
                ) : (
                  <Tag color="warning">У цели</Tag>
                )}
                <CommentCell comment={record.comment} onSave={(comment) => handleEditComment(record, comment)} />
              </span>
            </div>
            <div className="row-actions" onClick={e => e.stopPropagation()} style={{ flexShrink: 0, alignSelf: 'flex-start' }}>
              <AlertActionsDropdown item={item} alert={record} />
            </div>
          </div>
        );
      },
      maxWidth: 340,
      sorter: (a, b) => Number(a.targetPriceUsd) - Number(b.targetPriceUsd),
    },
  ], [item, handleEditComment, handleAlertClick]);

  return (
    <DataTable
      data={alerts}
      columnsConfig={columns}
      storageKey="watchlist-alerts-sorting"
    />
  );
});

export default WatchlistAlertsTable;
