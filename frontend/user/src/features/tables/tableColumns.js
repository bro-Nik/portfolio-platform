import { formatCurrency, formatPercentage, formatProfit, getColorClass } from '/app/src/utils/format';
import {
  getTransactionTypeColor,
  getAdjustedTransactionType,
  getTransactionTypeLabel,
  isTradeTransaction,
  isOutgoingTransaction,
} from '/app/src/modules/transaction/utils/type';

const DEFAULT_VALUE = '-';

export const createNameColumn = (openItem, itemType) => ({
  accessorKey: 'name',
  header: 'Название',
  cell: ({ row }) => (
    <div className="d-grid name text-average" onClick={() => openItem(row.original, itemType)}>
      <span>{row.original.name}</span>
      <span className="text-muted small-text capitalize">{row.original.market}</span>
      <span className="text-muted small-text">{row.original.assets?.length || 0} активов</span>
    </div>
  ),
  size: 300,
});

export const createAssetNameColumn = (openItem, itemType, parentId) => ({
  accessorFn: (row) => `${row.name} ${row.symbol}`,
  header: 'Актив',
  cell: ({ row }) => (
    <div className="text-average d-flex gap-2 name" onClick={() => openItem(row.original, itemType, parentId)}>
      <img className="img-asset-min" loading="lazy" src={row.original.image} />
      <span className="text-truncate" title={row.original.name}>{row.original.name}</span>
      <span className="text-muted text-uppercase">{row.original.symbol}</span>
    </div>
  ),
  size: 300,
});

export const createCostColumn = (hideCondition) => ({
  accessorKey: 'costNow',
  header: 'Стоимость',
  cell: ({ row }) => {
    // Условие скрытия
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;

    return formatCurrency(row.original.costNow);
  },
  size: 200,
});

export const createAveragePriceColumn = (hideCondition) => ({
  accessorKey: 'averagePrice',
  header: 'Средняя цена',
  cell: ({ row }) => {
    // Условие скрытия
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;

    return formatCurrency(row.original.averagePrice);
  },
  size: 200,
});

export const createQuantityColumn = (getTicker, hideCondition) => ({
  accessorKey: 'quantity',
  header: 'Количество',
  cell: ({ row }) => {
    // Условие скрытия
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;

    // Получаем тикер
    const ticker = getTicker ? getTicker(row.original) : '';

    return `${row.original.quantity}${ticker ? ' ' : ''}${ticker}`;
  },
  size: 200,
});

export const createShareColumn = (hideCondition) => ({
  accessorKey: 'share',
  header: 'Доля',
  cell: ({ row }) => {
    // Условие скрытия
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;

    return formatPercentage(row.original.share);
  },
  size: 120,
});

export const createProfitColumn = (hideCondition) => ({
  accessorKey: 'profit',
  header: 'Прибыль',
  cell: ({ row }) => {
    // Условие скрытия
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
    // Условие скрытия
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;

    return formatCurrency(row.original.invested);
  },
  size: 120,
});

export const createBuyOrdersColumn = (hideCondition) => ({
  accessorKey: 'buyOrders',
  header: 'В ордерах на покупку',
  cell: ({ row }) => {
    // Условие скрытия
    if (hideCondition && hideCondition(row.original)) return DEFAULT_VALUE;

    return formatCurrency(row.original.buyOrders || 0);
  },
  size: 120,
});

export const createSellOrdersColumn = (hideCondition) => ({
  accessorKey: 'sellOrders',
  header: 'В ордерах на продажу',
  cell: ({ row }) => {
    // Условие скрытия
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
        <span className="small-text text-muted">{transaction.date}</span>
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
      {/* В валюте пользователя */}
      {formatCurrency(transaction.priceUsd)}
      <br />
      {/* В валюте актива */}
      <span className="small-text text-muted">
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
      {/* В валюте пользователя */}
      {isOutgoingTransaction(transaction.type) ? '+' : '-'}
      {formatCurrency(transaction.priceUsd * transaction.quantity)}
      <br />
      {/* В валюте актива */}
      <span className={'small-text ' + (!isCounterTransaction(transaction) ? 'text-muted' : getTransactionTypeColor(getAdjustedTransactionType(transaction, isCounterTransaction)))}>
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
