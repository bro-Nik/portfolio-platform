import React, { memo, useMemo, useCallback } from 'react';
import DataTable from '/app/src/features/tables/DataTable';
import { formatCurrency } from '/app/src/utils/format';
import { useNavigation } from '/app/src/hooks/useNavigation';
import { useModalStore } from '/app/src/stores/modalStore';
import { BriefcaseIcon, WalletIcon } from '@heroicons/react/16/solid'
import TransactionEditModal from '/app/src/modules/transaction/modals/TransactionEdit';
import TransactionActionsDropdown from '/app/src/modules/transaction/components/TransactionActionsDropdown'
import { useTicker } from '/app/src/hooks/useTicker';
import { usePortfoliosData } from '/app/src/modules/portfolios/hooks/usePortfoliosData';
import { useWalletsData } from '/app/src/modules/wallets/hooks/useWalletsData';
import { isTradeTransaction, isTransferTransaction } from '/app/src/modules/transaction/utils/type';
import {
  createActionsColumn,
  createTransactionLinkColumn,
  createTransactionPriceColumn,
  createTransactionQuantityColumn,
  createTransactionSumColumn,
  createCommentColumn,
} from '/app/src/features/tables/tableColumns';

const AssetTable = memo(({ wallet, asset, transactions }) => {
  const { openModal } = useModalStore();
  const { openItem } = useNavigation();
  const { getTickerSymbol } = useTicker();
  const { getPortfolio } = usePortfoliosData();
  const { getWallet } = useWalletsData();

  const isCounterTransaction = useCallback((transaction) => {
    if (isTradeTransaction(transaction.type)) 
      return !(transaction.tickerId === asset.tickerId);
    if (isTransferTransaction(transaction.type)) 
      return !(transaction.walletId === wallet.id);
    return false;
  }, [asset.tickerId, wallet.id]);

  const handleTransactionClick = useCallback((transaction) => {
    openModal(TransactionEditModal, { tickerId: asset.tickerId, walletId: wallet.id, transaction });
  }, [openModal, asset, wallet.id]);

  const columns = useMemo(() => [
    createTransactionLinkColumn(getTickerSymbol, isCounterTransaction, handleTransactionClick),
    createTransactionPriceColumn(getTickerSymbol),
    createTransactionSumColumn(getTickerSymbol, isCounterTransaction),
    createTransactionQuantityColumn(getTickerSymbol, isCounterTransaction),
    {
      id: 'relation',
      header: 'Связь',
      cell: ({ row: { original: transaction } }) => {
        if (isTradeTransaction(transaction.type) && transaction.portfolioId) {
          const portfolio = getPortfolio(transaction.portfolioId);
          return (
            <div className="d-flex align-items-center gap-2 cursor-pointer" onClick={() => portfolio && openItem(portfolio, 'portfolio')}>
              <BriefcaseIcon />{portfolio?.name || 'Портфель удален'}
            </div>
          );
        }
        const relationWalletId = isCounterTransaction(transaction) ? transaction.walletId : transaction.wallet2Id
        if (isTransferTransaction(transaction.type) && relationWalletId) {
          const wallet2 = getWallet(relationWalletId);
          return (
            <div className="d-flex align-items-center gap-2 cursor-pointer" onClick={() => wallet2 && openItem(wallet2, 'wallet')}>
              <WalletIcon />{wallet2?.name || 'Кошелек удален'}
            </div>
          );
        }
        return '-';
      },
      size: 120,
    },
    createCommentColumn(),
    createActionsColumn(({ row }) => <TransactionActionsDropdown transaction={row.original} btn='icon' />),
  ], [
    getTickerSymbol, isCounterTransaction, handleTransactionClick, 
    getPortfolio, getWallet, openItem
  ]);

  return <DataTable data={transactions} columnsConfig={columns} />;
});

export default AssetTable;
