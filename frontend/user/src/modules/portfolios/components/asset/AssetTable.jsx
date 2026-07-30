import React, { memo, useMemo, useCallback } from 'react';
import DataTable from 'src/features/tables/DataTable';
import TransactionActionsDropdown from 'src/modules/transaction/components/TransactionActionsDropdown'
import TransactionEditModal from 'src/modules/transaction/modals/TransactionEdit';
import { useModalStore } from '@portfolio/shared';
import { usePortfoliosData } from 'src/modules/portfolios/hooks/usePortfoliosData';
import { useWalletsData } from 'src/modules/wallets/hooks/useWalletsData';
import { useNavigation } from 'src/hooks/useNavigation';
import { Briefcase, Wallet } from 'lucide-react'
import { isTradeTransaction, isTransferTransaction } from 'src/modules/transaction/utils/type';
import {
  createTransactionLinkColumn,
  createTransactionPriceColumn,
  createTransactionQuantityColumn,
  createTransactionSumColumn,
  createCommentColumn,
} from 'src/features/tables/tableColumns';

const AssetTable = memo(({ portfolio, asset, transactions }) => {
  const { openModal } = useModalStore();
  const { openItem } = useNavigation();
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
    if (asset.isArchived) return;
    openModal(TransactionEditModal, { tickerId: asset.tickerId, portfolioId: portfolio.id, transaction });
  }, [openModal, asset, portfolio.id]);

  const columns = useMemo(() => [
    createTransactionLinkColumn(isCounterTransaction, handleTransactionClick, asset.isArchived, (record) => <TransactionActionsDropdown portfolio={portfolio} asset={asset} transaction={record} />),
    createTransactionPriceColumn(),
    createTransactionSumColumn(isCounterTransaction),
    createTransactionQuantityColumn(isCounterTransaction),
    {
      key: 'relation',
      title: 'Связь',
      render: (_, record) => {
        if (record.portfolio2Id) {
          const portfolio2 = getPortfolio(record.portfolio2Id);
          return (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }} onClick={() => portfolio2 && openItem(portfolio2, 'portfolio')}>
              <Briefcase size={14} />{portfolio2?.name || 'Портфель удален'}
            </div>
          );
        }
        if (record.walletId) {
          const wallet = getWallet(record.walletId);
          return (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }} onClick={() => wallet && openItem(wallet, 'wallet')}>
              <Wallet size={14} />{wallet?.name || 'Кошелек удален'}
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

  return <DataTable data={transactions} columnsConfig={columns} storageKey="portfolio-asset-sorting" />;
});

export default AssetTable;
