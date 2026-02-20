import React, { memo, useMemo, useCallback } from 'react';
import DataTable from '/app/src/features/tables/DataTable';
import { formatCurrency } from '/app/src/utils/format';
import TransactionActionsDropdown from '/app/src/modules/transaction/components/TransactionActionsDropdown'
import TransactionEditModal from '/app/src/modules/transaction/modals/TransactionEdit';
import { useModalStore } from '/app/src/stores/modalStore';
import { useTicker } from '/app/src/hooks/useTicker';
import { usePortfoliosData } from '/app/src/modules/portfolios/hooks/usePortfoliosData';
import { useWalletsData } from '/app/src/modules/wallets/hooks/useWalletsData';
import { useNavigation } from '/app/src/hooks/useNavigation';
import { BriefcaseIcon, WalletIcon } from '@heroicons/react/16/solid'
import { isTradeTransaction, isTransferTransaction } from '/app/src/modules/transaction/utils/type';
import {
  createActionsColumn,
  createTransactionLinkColumn,
  createTransactionPriceColumn,
  createTransactionQuantityColumn,
  createTransactionSumColumn,
  createCommentColumn,
} from '/app/src/features/tables/tableColumns';

const AssetTable = memo(({ portfolio, asset, transactions }) => {
  const { openModal } = useModalStore();
  const { openItem } = useNavigation();
  const { getTickerSymbol } = useTicker();
  const { getPortfolio } = usePortfoliosData();
  const { getWallet } = useWalletsData();

  const isCounterTransaction = useCallback((transaction) => {
    if (isTradeTransaction(transaction.type)) 
      return !(transaction.tickerId === asset.tickerId);
    if (isTransferTransaction(transaction.type)) 
      return !(transaction.portfolioId === portfolio.id);
    return false;
  }, [asset.tickerId, portfolio.id]);

  const handleTransactionClick = useCallback((transaction) => {
    openModal(TransactionEditModal, { tickerId: asset.tickerId, portfolioId: portfolio.id, transaction });
  }, [openModal, asset, portfolio.id]);

  const columns = useMemo(() => [
    createTransactionLinkColumn(getTickerSymbol, isCounterTransaction, handleTransactionClick),
    createTransactionPriceColumn(getTickerSymbol),
    createTransactionSumColumn(getTickerSymbol, isCounterTransaction),
    createTransactionQuantityColumn(getTickerSymbol, isCounterTransaction),
    {
      id: 'relation',
      header: 'Связь',
      cell: ({ row: { original: transaction } }) => {
        if (transaction.portfolio2Id) {
          const portfolio2 = getPortfolio(transaction.portfolio2Id);
          return (
            <div className="d-flex align-items-center gap-2 cursor-pointer" onClick={() => portfolio2 && openItem(portfolio2, 'portfolio')}>
              <BriefcaseIcon />{portfolio2?.name || 'Портфель удален'}
            </div>
          );
        }
        if (transaction.walletId) {
          const wallet = getWallet(transaction.walletId);
          return (
            <div className="d-flex align-items-center gap-2 cursor-pointer" onClick={() => wallet && openItem(wallet, 'wallet')}>
              <WalletIcon />{wallet?.name || 'Кошелек удален'}
            </div>
          );
        }
        return '-';
      },
      size: 120,
    },
    createCommentColumn(),
    createActionsColumn(({ row }) => <TransactionActionsDropdown portfolio={portfolio} asset={asset} transaction={row.original} btn='icon' />),
  ], [
    getTickerSymbol, isCounterTransaction, handleTransactionClick, 
    getPortfolio, getWallet, openItem
  ]);

  return <DataTable data={transactions} columnsConfig={columns} />;
});

export default AssetTable;
