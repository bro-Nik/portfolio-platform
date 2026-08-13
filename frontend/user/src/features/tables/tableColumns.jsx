import { formatCurrency, formatCurrencyFromUsd, formatPercentage, formatProfit, formatDateTime, formatQuantity, formatUsdValueOrDash, getColorClass } from 'src/utils/format';
import {
  getTransactionTypeColor,
  getAdjustedTransactionType,
  getTransactionTypeLabel,
  isTradeTransaction,
  isOutgoingTransaction,
} from 'src/modules/transaction/utils/type';
import TagBadges from 'src/modules/tags/components/TagBadges';
import TickerAvatar from 'src/components/TickerAvatar';
import CommentCell from '../forms/CommentCell';

const DEFAULT_VALUE = '-';

const mutedStyle = { color: 'var(--text-muted)' };
const smallTextStyle = { fontSize: '12px' };

export const createNameColumn = (openItem, itemType, actions, onEditComment) => ({
  dataIndex: 'name',
  title: 'Название',
  fixed: 'left',
  render: (_, record) => (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
      <div style={{ display: 'grid', flex: 1 }}>
        <span style={{ display: 'flex', alignItems: 'flex-start', cursor: 'pointer' }} title={record.name} onClick={() => openItem(record, itemType)}>
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flexShrink: 1, minWidth: 0 }}>
            {record.name}
          </span>
          {record.isArchived && <span style={{ ...mutedStyle, fontSize: 10, whiteSpace: 'nowrap', flexShrink: 0, marginTop: 1, marginLeft: 4 }}>Архивный</span>}
        </span>
        <span style={{ ...mutedStyle, ...smallTextStyle, textTransform: 'capitalize' }}>{record.market}</span>
        <span style={{ display: 'flex', alignItems: 'center', ...mutedStyle, ...smallTextStyle, gap: 8 }}>
          {record.assets?.length || 0} активов
          <CommentCell comment={record.comment} onSave={(comment) => onEditComment(record, comment)}/>
        </span>
        <TagBadges tags={record.tags} entityType={itemType} entityId={record.id} assignedTags={record.tags} />
      </div>
      {actions && <div className="row-actions" onClick={e => e.stopPropagation()} style={{ flexShrink: 0, alignSelf: 'flex-start' }}>{actions(record)}</div>}
    </div>
  ),
  maxWidth: 300,
  sorter: (a, b) => (a.name || '').localeCompare(b.name || ''),
});

export const createAssetNameColumn = (openItem, itemType, parentId, actions) => ({
  key: 'name',
  title: 'Актив',
  fixed: 'left',
  render: (_, record) => (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
      <div style={{ display: 'flex', gap: 8, flex: 1 }}>
        <TickerAvatar src={record.image} symbol={record.symbol} size={24} />
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ display: 'flex', alignItems: 'flex-start', cursor: 'pointer' }} onClick={() => openItem(record, itemType, parentId)}>
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flexShrink: 1, minWidth: 0 }} title={record.name}>{record.name}</span>
            <span style={{ ...mutedStyle, textTransform: 'uppercase', marginLeft: 4, flexShrink: 0 }}>{record.symbol}</span>
            {record.isArchived && <span style={{ ...mutedStyle, fontSize: 10, whiteSpace: 'nowrap', flexShrink: 0, marginLeft: 4, marginTop: 1 }}>Архивный</span>}
          </span>
          <TagBadges tags={record.tags} entityType={itemType} entityId={record.id} parentId={parentId} assignedTags={record.tags} />
        </div>
      </div>
      {actions && <div className="row-actions" onClick={e => e.stopPropagation()} style={{ flexShrink: 0, alignSelf: 'flex-start' }}>{actions(record)}</div>}
    </div>
  ),
  maxWidth: 300,
  sorter: (a, b) => (a.name || '').localeCompare(b.name || ''),
});

export const createCostColumn = () => ({
  dataIndex: 'costNow',
  title: 'Стоимость',
  render: (value) => formatUsdValueOrDash(value),
  width: 200,
  sorter: (a, b) => a.costNow - b.costNow,
});

export const createShareColumn = () => ({
  dataIndex: 'share',
  title: 'Доля',
  render: (value) => value > 0 ? formatPercentage(value) : DEFAULT_VALUE,
  width: 120,
  sorter: (a, b) => a.share - b.share,
});

export const createProfitColumn = () => ({
  dataIndex: 'profit',
  title: 'Прибыль',
  render: (value, record) => {
    if (value == null || value === 0) return DEFAULT_VALUE;
    return (
      <span className={getColorClass(value)}>
        {formatProfit(value, record.invested, record.totalInvested)}
      </span>
    );
  },
  width: 120,
  sorter: (a, b) => (a.profit ?? 0) - (b.profit ?? 0),
});

export const createInvestedColumn = () => ({
  dataIndex: 'invested',
  title: 'Вложено',
  render: (value) => formatUsdValueOrDash(value),
  width: 120,
  sorter: (a, b) => a.invested - b.invested,
});

export const createBuyOrdersColumn = () => ({
  dataIndex: 'buyOrders',
  title: 'Ордера на покупку',
  render: (value) => formatUsdValueOrDash(value),
  width: 120,
  sorter: (a, b) => (a.buyOrders || 0) - (b.buyOrders || 0),
});

export const createActionsColumn = (renderElement) => ({
  key: 'actions',
  title: '',
  render: (_, record) => renderElement({ row: { original: record } }),
  width: 100,
});

export const createTransactionLinkColumn = (isCounterTransaction, onClick, disabled, actions, onEditComment) => ({
  key: 'transactionLink',
  title: 'Тип',
  render: (_, record) => {
    const colorClassName = getTransactionTypeColor(getAdjustedTransactionType(record, isCounterTransaction));
    return (
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
        <div style={{ flex: 1 }}>
          <span
            className={colorClassName}
            style={{ cursor: disabled ? 'default' : 'pointer' }}
            onClick={() => { if (!disabled) onClick(record); }}
          >
            {getTransactionTypeLabel(record, isCounterTransaction)}
            {record.order ? ' (Ордер)' : ''}
          </span>
          <br />
          <span style={{ display: 'flex', alignItems: 'center', ...smallTextStyle, ...mutedStyle, gap: 8 }}>
            {formatDateTime(record.date)}
            <CommentCell comment={record.comment} onSave={(comment) => onEditComment(record, comment)}/>
          </span>
        </div>
        {actions && <div className="row-actions" onClick={e => e.stopPropagation()} style={{ flexShrink: 0, alignSelf: 'flex-start' }}>{actions(record)}</div>}
      </div>
    );
  },
  width: 200,
  sorter: (a, b) => (a.date || '').localeCompare(b.date || ''),
});

export const createTransactionPriceColumn = () => ({
  dataIndex: 'price',
  title: 'Цена',
  render: (_, record) => {
    if (isTradeTransaction(record.type)) return (
      <>
      {formatCurrencyFromUsd(record.priceUsd, true)}
      <br />
      <span style={{ ...smallTextStyle, ...mutedStyle }}>
        {formatCurrency(record.price, record.ticker2Symbol, undefined, true)}
      </span>
      </>
    );
    return '-';
  },
  width: 200,
});

export const createTransactionSumColumn = (isCounterTransaction) => ({
  dataIndex: 'quantity2',
  title: 'Сумма',
  render: (_, record) => {
    if (isTradeTransaction(record.type)) return (
      <>
      {isOutgoingTransaction(record.type) ? '+' : '-'}
      {formatCurrencyFromUsd(record.priceUsd * record.quantity)}
      <br />
      <span style={{ ...smallTextStyle, ...(!isCounterTransaction(record) ? mutedStyle : { color: getTransactionTypeColor(getAdjustedTransactionType(record, isCounterTransaction)) }) }}>
        {isOutgoingTransaction(record.type) ? '+' : '-'}{formatCurrency(record.quantity2, record.ticker2Symbol, undefined, true)}
      </span>
      </>
    );
    return '-';
  },
  width: 200,
});

export const createTransactionQuantityColumn = (isCounterTransaction) => ({
  dataIndex: 'quantity',
  title: 'Количество',
  render: (_, record) => {
    const adjustedType = getAdjustedTransactionType(record, isCounterTransaction);
    return (
      <span className={isCounterTransaction(record) && isTradeTransaction(record) ? '' : getTransactionTypeColor(adjustedType)}>
        {isOutgoingTransaction(adjustedType) ? '-' : '+'}{formatQuantity(record.quantity)} {record.tickerSymbol?.toUpperCase()}
      </span>
    );
  },
  width: 200,
  sorter: (a, b) => a.quantity - b.quantity,
});
