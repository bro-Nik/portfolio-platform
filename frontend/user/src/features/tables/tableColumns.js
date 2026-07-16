import { formatCurrency, formatPercentage, formatProfit, getColorClass } from '/app/src/utils/format';
import {
  getTransactionTypeColor,
  getAdjustedTransactionType,
  getTransactionTypeLabel,
  isTradeTransaction,
  isOutgoingTransaction,
} from '/app/src/modules/transaction/utils/type';
import TagBadges from '/app/src/modules/portfolios/components/TagBadges';

const DEFAULT_VALUE = '-';

const mutedStyle = { color: 'rgba(0,0,0,0.45)' };
const smallTextStyle = { fontSize: '12px' };

export const createNameColumn = (openItem, itemType) => ({
  dataIndex: 'name',
  title: 'Название',
  render: (_, record) => (
    <div style={{ display: 'grid' }} onClick={() => openItem(record, itemType)}>
      <span>{record.name}</span>
      <span style={{ ...mutedStyle, ...smallTextStyle, textTransform: 'capitalize' }}>{record.market}</span>
      <span style={{ ...mutedStyle, ...smallTextStyle }}>{record.assets?.length || 0} активов</span>
      <TagBadges tags={record.tags} />
    </div>
  ),
  width: 300,
  sorter: (a, b) => (a.name || '').localeCompare(b.name || ''),
});

export const createAssetNameColumn = (openItem, itemType, parentId) => ({
  key: 'name',
  title: 'Актив',
  render: (_, record) => (
    <div style={{ display: 'flex', gap: 8 }} onClick={() => openItem(record, itemType, parentId)}>
      <img className="img-asset-min" loading="lazy" src={record.image} />
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <span>
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={record.name}>{record.name}</span>
          <span style={{ ...mutedStyle, textTransform: 'uppercase', marginLeft: 4 }}>{record.symbol}</span>
        </span>
        <TagBadges tags={record.tags} />
      </div>
    </div>
  ),
  width: 300,
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
    return formatCurrency(value);
  },
  width: 200,
  sorter: (a, b) => a.averagePrice - b.averagePrice,
});

export const createQuantityColumn = (getTicker, hideCondition) => ({
  dataIndex: 'quantity',
  title: 'Количество',
  render: (value, record) => {
    if (hideCondition && hideCondition(record)) return DEFAULT_VALUE;
    const ticker = getTicker ? getTicker(record) : '';
    return `${value}${ticker ? ' ' : ''}${ticker}`;
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
    return (
      <span className={getColorClass(value)}>
        {formatProfit(value, record.invested, record.totalInvested)}
      </span>
    );
  },
  width: 120,
  sorter: (a, b) => a.profit - b.profit,
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

export const createTransactionLinkColumn = (getTicker, isCounterTransaction, onClick) => ({
  key: 'transactionLink',
  title: 'Тип',
  render: (_, record) => {
    const colorClassName = getTransactionTypeColor(getAdjustedTransactionType(record, isCounterTransaction));
    return (
      <div onClick={() => onClick(record)}>
        <span className={colorClassName}>
          {getTransactionTypeLabel(record, isCounterTransaction, getTicker)}
          {record.order ? ' (Ордер)' : ''}
        </span>
        <br />
        <span style={{ ...smallTextStyle, ...mutedStyle }}>{record.date}</span>
      </div>
    );
  },
  width: 200,
  sorter: (a, b) => (a.date || '').localeCompare(b.date || ''),
});

export const createTransactionPriceColumn = (getTicker) => ({
  dataIndex: 'price',
  title: 'Цена',
  render: (_, record) => {
    if (isTradeTransaction(record.type)) return (
      <>
      {formatCurrency(record.priceUsd)}
      <br />
      <span style={{ ...smallTextStyle, ...mutedStyle }}>
        {formatCurrency(record.price, getTicker(record.ticker2Id))}
      </span>
      </>
    );
    return '-';
  },
  width: 200,
});

export const createTransactionSumColumn = (getTicker, isCounterTransaction) => ({
  dataIndex: 'quantity2',
  title: 'Сумма',
  render: (_, record) => {
    if (isTradeTransaction(record.type)) return (
      <>
      {isOutgoingTransaction(record.type) ? '+' : '-'}
      {formatCurrency(record.priceUsd * record.quantity)}
      <br />
      <span style={{ ...smallTextStyle, ...(!isCounterTransaction(record) ? mutedStyle : { color: getTransactionTypeColor(getAdjustedTransactionType(record, isCounterTransaction)) }) }}>
        {isOutgoingTransaction(record.type) ? '+' : '-'}{formatCurrency(record.quantity2, getTicker(record.ticker2Id))}
      </span>
      </>
    );
    return '-';
  },
  width: 200,
});

export const createTransactionQuantityColumn = (getTicker, isCounterTransaction) => ({
  dataIndex: 'quantity',
  title: 'Количество',
  render: (_, record) => {
    const adjustedType = getAdjustedTransactionType(record, isCounterTransaction);
    return (
      <span className={isCounterTransaction(record) && isTradeTransaction(record) ? '' : getTransactionTypeColor(adjustedType)}>
        {isOutgoingTransaction(adjustedType) ? '-' : '+'}{record.quantity} {getTicker(record.tickerId)}
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
