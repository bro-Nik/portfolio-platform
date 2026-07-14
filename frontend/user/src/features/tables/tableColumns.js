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
  accessorKey: 'name',
  header: 'Название',
  cell: ({ row }) => (
    <div style={{ display: 'grid' }} onClick={() => openItem(row.original, itemType)}>
      <span>{row.original.name}</span>
      <span style={{ ...mutedStyle, ...smallTextStyle, textTransform: 'capitalize' }}>{row.original.market}</span>
      <span style={{ ...mutedStyle, ...smallTextStyle }}>{row.original.assets?.length || 0} активов</span>
      <TagBadges tags={row.original.tags} />
    </div>
  ),
  size: 300,
});

export const createAssetNameColumn = (openItem, itemType, parentId) => ({
  accessorFn: (row) => `${row.name} ${row.symbol}`,
  header: 'Актив',
  cell: ({ row }) => (
    <div style={{ display: 'flex', gap: 8 }} onClick={() => openItem(row.original, itemType, parentId)}>
      <img className="img-asset-min" loading="lazy" src={row.original.image} />
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <span>
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={row.original.name}>{row.original.name}</span>
          <span style={{ ...mutedStyle, textTransform: 'uppercase', marginLeft: 4 }}>{row.original.symbol}</span>
        </span>
        <TagBadges tags={row.original.tags} />
      </div>
    </div>
  ),
  size: 300,
});

export const createCostColumn = (hideCondition) => ({
  accessorKey: 'costNow',
  header: 'Стоимость',
  cell: ({ row }) => {
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;
    return formatCurrency(row.original.costNow);
  },
  size: 200,
});

export const createAveragePriceColumn = (hideCondition) => ({
  accessorKey: 'averagePrice',
  header: 'Средняя цена',
  cell: ({ row }) => {
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;
    return formatCurrency(row.original.averagePrice);
  },
  size: 200,
});

export const createQuantityColumn = (getTicker, hideCondition) => ({
  accessorKey: 'quantity',
  header: 'Количество',
  cell: ({ row }) => {
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;
    const ticker = getTicker ? getTicker(row.original) : '';
    return `${row.original.quantity}${ticker ? ' ' : ''}${ticker}`;
  },
  size: 200,
});

export const createShareColumn = (hideCondition) => ({
  accessorKey: 'share',
  header: 'Доля',
  cell: ({ row }) => {
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;
    return formatPercentage(row.original.share);
  },
  size: 120,
});

export const createProfitColumn = (hideCondition) => ({
  accessorKey: 'profit',
  header: 'Прибыль',
  cell: ({ row }) => {
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;
    return (
      <span className={getColorClass(row.original.profit)}>
        {formatProfit(row.original.profit, row.original.invested, row.original.totalInvested)}
      </span>
    );
  },
  size: 120,
});

export const createInvestedColumn = (hideCondition) => ({
  accessorKey: 'invested',
  header: 'Вложено',
  cell: ({ row }) => {
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;
    return formatCurrency(row.original.invested);
  },
  size: 120,
});

export const createBuyOrdersColumn = (hideCondition) => ({
  accessorKey: 'buyOrders',
  header: 'В ордерах на покупку',
  cell: ({ row }) => {
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;
    return formatCurrency(row.original.buyOrders || 0);
  },
  size: 120,
});

export const createSellOrdersColumn = (hideCondition) => ({
  accessorKey: 'sellOrders',
  header: 'В ордерах на продажу',
  cell: ({ row }) => {
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;
    return formatCurrency(row.original.sellOrders || 0);
  },
  size: 120,
});

export const createActionsColumn = (renderElement) => ({
  id: 'actions',
  header: '',
  cell: (props) => renderElement(props),
  size: 100,
});

export const createTransactionLinkColumn = (getTicker, isCounterTransaction, onClick) => ({
  id: 'transactionLink',
  header: 'Тип',
  cell: ({ row: { original: transaction } }) => {
    const colorClassName = getTransactionTypeColor(getAdjustedTransactionType(transaction, isCounterTransaction));
    return (
      <div onClick={() => onClick(transaction)}>
        <span className={colorClassName}>
          {getTransactionTypeLabel(transaction, isCounterTransaction, getTicker)}
          {transaction.order ? ' (Ордер)' : ''}
        </span>
        <br />
        <span style={{ ...smallTextStyle, ...mutedStyle }}>{transaction.date}</span>
      </div>
    );
  },
  size: 200,
});

export const createTransactionPriceColumn = (getTicker) => ({
  accessorKey: 'price',
  header: 'Цена',
  cell: ({ row: { original: transaction } }) => {
    if (isTradeTransaction(transaction.type)) return (
      <>
      {formatCurrency(transaction.priceUsd)}
      <br />
      <span style={{ ...smallTextStyle, ...mutedStyle }}>
        {formatCurrency(transaction.price, getTicker(transaction.ticker2Id))}
      </span>
      </>
    );
    return '-';
  },
  size: 200,
});

export const createTransactionSumColumn = (getTicker, isCounterTransaction) => ({
  accessorKey: 'quantity2',
  header: 'Сумма',
  cell: ({ row: { original: transaction } }) => {
    if (isTradeTransaction(transaction.type)) return (
      <>
      {isOutgoingTransaction(transaction.type) ? '+' : '-'}
      {formatCurrency(transaction.priceUsd * transaction.quantity)}
      <br />
      <span style={{ ...smallTextStyle, ...(!isCounterTransaction(transaction) ? mutedStyle : { color: getTransactionTypeColor(getAdjustedTransactionType(transaction, isCounterTransaction)) }) }}>
        {isOutgoingTransaction(transaction.type) ? '+' : '-'}{formatCurrency(transaction.quantity2, getTicker(transaction.ticker2Id))}
      </span>
      </>
    );
    return '-';
  },
  size: 200,
});

export const createTransactionQuantityColumn = (getTicker, isCounterTransaction) => ({
  accessorKey: 'quantity',
  header: 'Количество',
  cell: ({ row: { original: transaction } }) => {
    const adjustedType = getAdjustedTransactionType(transaction, isCounterTransaction);
    return (
      <span className={isCounterTransaction(transaction) && isTradeTransaction(transaction) ? '' : getTransactionTypeColor(adjustedType)}>
        {isOutgoingTransaction(adjustedType) ? '-' : '+'}{transaction.quantity} {getTicker(transaction.tickerId)}
      </span>
    );
  },
  size: 200,
});

export const createCommentColumn = () => ({
  accessorKey: 'comment',
  header: 'Комментарий',
  cell: ({ row: { original: obj } }) => obj.comment,
  size: 120,
});
