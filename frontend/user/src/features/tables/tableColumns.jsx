import { formatCurrency, formatPercentage, formatProfit, formatDateTime, formatQuantity, getColorClass } from 'src/utils/format';
import {
  getTransactionTypeColor,
  getAdjustedTransactionType,
  getTransactionTypeLabel,
  isTradeTransaction,
  isOutgoingTransaction,
} from 'src/modules/transaction/utils/type';
import TagBadges from 'src/modules/tags/components/TagBadges';

const DEFAULT_VALUE = '-';

const mutedStyle = { color: 'var(--text-muted)' };
const smallTextStyle = { fontSize: '12px' };

export const createNameColumn = (openItem, itemType, actions) => ({
  dataIndex: 'name',
  title: 'Название',
  fixed: 'left',
  render: (_, record) => (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
      <div style={{ display: 'grid', flex: 1 }} onClick={() => openItem(record, itemType)}>
        <span style={{ display: 'flex', alignItems: 'flex-start', cursor: 'pointer' }} title={record.name}>
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flexShrink: 1, minWidth: 0 }}>
            {record.name}
          </span>
          {record.isArchived && <span style={{ ...mutedStyle, fontSize: 10, whiteSpace: 'nowrap', flexShrink: 0, marginTop: 1, marginLeft: 4 }}>Архивный</span>}
        </span>
        <span style={{ ...mutedStyle, ...smallTextStyle, textTransform: 'capitalize' }}>{record.market}</span>
        <span style={{ ...mutedStyle, ...smallTextStyle }}>{record.assets?.length || 0} активов</span>
        <TagBadges tags={record.tags} entityType={itemType} entityId={record.id} assignedTags={record.tags} />
      </div>
      {actions && <div className="row-actions" onClick={e => e.stopPropagation()} style={{ flexShrink: 0, alignSelf: 'flex-start' }}>{actions(record)}</div>}
    </div>
  ),
  maxWidth: 300,
  sorter: (a, b) => (a.name || '').localeCompare(b.name || ''),
});

export const createAssetNameColumn = (openItem, itemType, parentId) => ({
  key: 'name',
  title: 'Актив',
  fixed: 'left',
  render: (_, record) => (
    <div style={{ display: 'flex', gap: 8 }} onClick={() => openItem(record, itemType, parentId)}>
      <img className="img-asset-min" loading="lazy" src={record.image} style={{ cursor: 'pointer' }} />
      <div style={{ display: 'flex', flexDirection: 'column', cursor: 'pointer' }}>
        <span style={{ display: 'flex', alignItems: 'flex-start' }}>
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flexShrink: 1, minWidth: 0 }} title={record.name}>{record.name}</span>
          <span style={{ ...mutedStyle, textTransform: 'uppercase', marginLeft: 4, flexShrink: 0 }}>{record.symbol}</span>
          {record.isArchived && <span style={{ ...mutedStyle, fontSize: 10, whiteSpace: 'nowrap', flexShrink: 0, marginLeft: 4, marginTop: 1 }}>Архивный</span>}
        </span>
        <TagBadges tags={record.tags} entityType={itemType} entityId={record.id} parentId={parentId} assignedTags={record.tags} />
      </div>
    </div>
  ),
  maxWidth: 300,
  sorter: (a, b) => (a.name || '').localeCompare(b.name || ''),
});

export const createCostColumn = (hideCondition) => ({
  dataIndex: 'costNow',
  title: 'Стоимость',
  render: (value, record) => {
    if (hideCondition && hideCondition(record)) return DEFAULT_VALUE;
    return formatCurrency(value);
  },
  width: 200,
  sorter: (a, b) => a.costNow - b.costNow,
});

export const createAveragePriceColumn = (hideCondition) => ({
  dataIndex: 'averagePrice',
  title: 'Средняя цена',
  render: (value, record) => {
    if (hideCondition && hideCondition(record)) return DEFAULT_VALUE;
    if (value == null) return DEFAULT_VALUE;
    return formatCurrency(value);
  },
  width: 200,
  sorter: (a, b) => (a.averagePrice ?? 0) - (b.averagePrice ?? 0),
});

export const createQuantityColumn = (getTicker, hideCondition) => ({
  dataIndex: 'quantity',
  title: 'Количество',
  render: (value, record) => {
    if (hideCondition && hideCondition(record)) return DEFAULT_VALUE;
    const ticker = getTicker ? getTicker(record) : '';
    return `${formatQuantity(value)}${ticker ? ' ' : ''}${ticker}`;
  },
  width: 200,
  sorter: (a, b) => a.quantity - b.quantity,
});

export const createShareColumn = (hideCondition) => ({
  dataIndex: 'share',
  title: 'Доля',
  render: (value, record) => {
    if (hideCondition && hideCondition(record)) return DEFAULT_VALUE;
    return formatPercentage(value);
  },
  width: 120,
  sorter: (a, b) => a.share - b.share,
});

export const createProfitColumn = (hideCondition) => ({
  dataIndex: 'profit',
  title: 'Прибыль',
  render: (value, record) => {
    if (hideCondition && hideCondition(record)) return DEFAULT_VALUE;
    if (value == null) return DEFAULT_VALUE;
    return (
      <span className={getColorClass(value)}>
        {formatProfit(value, record.invested, record.totalInvested)}
      </span>
    );
  },
  width: 120,
  sorter: (a, b) => (a.profit ?? 0) - (b.profit ?? 0),
});

export const createInvestedColumn = (hideCondition) => ({
  dataIndex: 'invested',
  title: 'Вложено',
  render: (value, record) => {
    if (hideCondition && hideCondition(record)) return DEFAULT_VALUE;
    return formatCurrency(value);
  },
  width: 120,
  sorter: (a, b) => a.invested - b.invested,
});

export const createBuyOrdersColumn = (hideCondition) => ({
  dataIndex: 'buyOrders',
  title: 'В ордерах на покупку',
  render: (value, record) => {
    if (hideCondition && hideCondition(record)) return DEFAULT_VALUE;
    return formatCurrency(value || 0);
  },
  width: 120,
  sorter: (a, b) => (a.buyOrders || 0) - (b.buyOrders || 0),
});

export const createSellOrdersColumn = (hideCondition) => ({
  dataIndex: 'sellOrders',
  title: 'В ордерах на продажу',
  render: (value, record) => {
    if (hideCondition && hideCondition(record)) return DEFAULT_VALUE;
    return formatCurrency(value || 0);
  },
  width: 120,
  sorter: (a, b) => (a.sellOrders || 0) - (b.sellOrders || 0),
});

export const createActionsColumn = (renderElement) => ({
  key: 'actions',
  title: '',
  render: (_, record) => renderElement({ row: { original: record } }),
  width: 100,
});

export const createTransactionLinkColumn = (isCounterTransaction, onClick, disabled, actions) => ({
  key: 'transactionLink',
  title: 'Тип',
  render: (_, record) => {
    const colorClassName = getTransactionTypeColor(getAdjustedTransactionType(record, isCounterTransaction));
    return (
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
        <div onClick={() => !disabled && onClick(record)} style={{ cursor: disabled ? 'default' : 'pointer', flex: 1 }}>
          <span className={colorClassName}>
            {getTransactionTypeLabel(record, isCounterTransaction)}
            {record.order ? ' (Ордер)' : ''}
          </span>
          <br />
          <span style={{ ...smallTextStyle, ...mutedStyle }}>{formatDateTime(record.date)}</span>
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
      {formatCurrency(record.priceUsd)}
      <br />
      <span style={{ ...smallTextStyle, ...mutedStyle }}>
        {formatCurrency(record.price, record.ticker2Symbol)}
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
      {formatCurrency(record.priceUsd * record.quantity)}
      <br />
      <span style={{ ...smallTextStyle, ...(!isCounterTransaction(record) ? mutedStyle : { color: getTransactionTypeColor(getAdjustedTransactionType(record, isCounterTransaction)) }) }}>
        {isOutgoingTransaction(record.type) ? '+' : '-'}{formatCurrency(record.quantity2, record.ticker2Symbol)}
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

export const createCommentColumn = () => ({
  dataIndex: 'comment',
  title: 'Комментарий',
  render: (value) => value || '-',
  width: 120,
});
