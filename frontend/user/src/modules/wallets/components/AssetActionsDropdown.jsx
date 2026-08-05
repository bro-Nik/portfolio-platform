import { Tooltip } from 'antd';
import { useModalStore } from '@portfolio/shared';
import {
  Inbox,
  Undo2,
  Trash2,
  ExternalLink,
  Send,
} from 'lucide-react'
import ActionsDropdown from 'src/features/dropdowns/ActionsDropdown';
import TagManagerSelect from 'src/modules/tags/components/TagManagerSelect';
import { getTradingViewUrl } from 'src/utils/format';
import { useWalletMutations } from 'src/modules/wallets/hooks/useWalletMutations';
import TransactionEditModal from 'src/modules/transaction/modals/TransactionEdit';

const AssetActionsDropdown = ({ wallet, asset }) => {
  const { openModal } = useModalStore();
  const { archiveWalletAsset, unarchiveWalletAsset } = useWalletMutations();

  const handleArchive = async () => {
    await archiveWalletAsset.mutateAsync({ walletId: wallet.id, assetId: asset.id });
  };

  const handleUnarchive = async () => {
    await unarchiveWalletAsset.mutateAsync({ walletId: wallet.id, assetId: asset.id });
  };

  const menuItems = [
    {
      key: 'send',
      icon: <Send size={16} />,
      label: 'Отправить',
      disabled: asset.isArchived,
      onClick: () => openModal(TransactionEditModal, { tickerId: asset.tickerId, walletId: wallet.id }),
    },
    {
      key: 'tradingview',
      icon: <ExternalLink size={16} />,
      label: 'Посмотреть на TradingView',
      onClick: () => window.open(getTradingViewUrl(asset.symbol, wallet.market), '_blank', 'noopener,noreferrer'),
    },
    {
      type: 'divider',
    },
    {
      key: 'tags',
      label: <TagManagerSelect trigger="menu" entityType="wallet_asset" entityId={asset?.id} assignedTags={asset?.tags} />,
    },
    {
      type: 'divider',
    },
    ...(asset.isArchived
      ? [{
          key: 'unarchive',
          icon: <Undo2 size={16} />,
          label: 'Разархивировать',
          onClick: handleUnarchive,
        }]
      : [{
          key: 'archive',
          icon: <Inbox size={16} />,
          label: 'Архивировать',
          onClick: handleArchive,
        }]
    ),
    {
      key: 'delete',
      icon: <Trash2 size={16} />,
      label: asset.hasTransactions ? <Tooltip title="Нельзя удалить — есть транзакции"><span>Удалить</span></Tooltip> : 'Удалить',
      danger: true,
      disabled: asset.hasTransactions,
    },
  ];

  return <ActionsDropdown items={menuItems} />;
};

export default AssetActionsDropdown;
