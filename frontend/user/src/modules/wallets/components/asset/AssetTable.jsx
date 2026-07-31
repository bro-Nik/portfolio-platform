import React, { memo, useMemo, useCallback } from 'react';
import DataTable from 'src/features/tables/DataTable';
import { useNavigation } from 'src/hooks/useNavigation';
import { useModalStore } from '@portfolio/shared';
import { Briefcase, Wallet } from 'lucide-react'
import TransactionEditModal from 'src/modules/transaction/modals/TransactionEdit';
import TransactionActionsDropdown from 'src/modules/transaction/components/TransactionActionsDropdown'
import { usePortfoliosData } from 'src/modules/portfolios/hooks/usePortfoliosData';
import { useWalletsData } from 'src/modules/wallets/hooks/useWalletsData';
import { isTradeTransaction, isTransferTransaction } from 'src/modules/transaction/utils/type';
import {
  createTransactionLinkColumn,
  createTransactionPriceColumn,
  createTransactionQuantityColumn,
  createTransactionSumColumn,
  createCommentColumn,
} from 'src/features/tables/tableColumns';

const AssetTable = memo(({ wallet, asset, transactions }) => {
  const { openModal } = useModalStore();
  const { openItem } = useNavigation();
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
    if (asset.isArchived) return;
    openModal(TransactionEditModal, { tickerId: asset.tickerId, walletId: wallet.id, transaction });
  }, [openModal, asset, wallet.id]);

  const columns = useMemo(() => [
    createTransactionLinkColumn(isCounterTransaction, handleTransactionClick, asset.isArchived, (record) => <TransactionActionsDropdown wallet={wallet} asset={asset} transaction={record} />),
    createTransactionPriceColumn(),
    createTransactionSumColumn(isCounterTransaction),
    createTransactionQuantityColumn(isCounterTransaction),
    {
      key: 'relation',
      title: 'Связь',
      render: (_, record) => {
        if (isTradeTransaction(record.type) && record.portfolioId) {
          const portfolio = getPortfolio(record.portfolioId);
          return (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }} onClick={() => portfolio && openItem(portfolio, 'portfolio')}>
              <Briefcase size={14} />{portfolio?.name || 'Портфель удален'}
            </div>
          );
        }
        const relationWalletId = isCounterTransaction(record) ? record.walletId : record.wallet2Id
        if (isTransferTransaction(record.type) && relationWalletId) {
          const wallet2 = getWallet(relationWalletId);
          return (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }} onClick={() => wallet2 && openItem(wallet2, 'wallet')}>
              <Wallet size={14} />{wallet2?.name || 'Кошелек удален'}
            </div>
          );
        }
        return '-';
      },
      width: 120,
    },
    createCommentColumn(),
  ], [
    isCounterTransaction, handleTransactionClick,
    getPortfolio, getWallet, openItem
  ]);

  return <DataTable data={transactions} columnsConfig={columns} storageKey="wallet-asset-sorting" />;
});

export default AssetTable;
