import { useModalStore } from '@portfolio/shared';
import { Tooltip } from 'antd';
import {
  Inbox,
  Undo2,
  Pencil,
  Copy,
  Trash2,
  ExternalLink,
} from 'lucide-react'
import ActionsDropdown from 'src/features/dropdowns/ActionsDropdown';
import WalletEditModal from './modals/WalletEdit';
import WalletDeleteModal from './modals/WalletDelete';
import TagManagerSelect from 'src/modules/tags/components/TagManagerSelect';
import { useWalletMutations } from 'src/modules/wallets/hooks/useWalletMutations';

const WalletActionsDropdown = ({ wallet, onUpdate }) => {
  const { openModal } = useModalStore();
  const { archiveWallet, unarchiveWallet } = useWalletMutations();

  const handleArchive = async () => {
    await archiveWallet.mutateAsync(wallet.id);
  };

  const handleUnarchive = async () => {
    await unarchiveWallet.mutateAsync(wallet.id);
  };

  const menuItems = [
    {
      key: 'edit',
      icon: <Pencil size={16} />,
      label: 'Редактировать',
      disabled: wallet.isArchived,
      onClick: () => openModal(WalletEditModal, { wallet }),
    },
    {
      key: 'duplicate',
      icon: <Copy size={16} />,
      label: 'Дублировать',
      disabled: true,
    },
    {
      key: 'export',
      icon: <ExternalLink size={16} />,
      label: 'Экспортировать',
      disabled: true,
    },
    {
      type: 'divider',
    },
    {
      key: 'tags',
      label: <TagManagerSelect trigger="menu" entityType="wallet" entityId={wallet?.id} assignedTags={wallet?.tags} />,
    },
    {
      type: 'divider',
    },
    ...(wallet.isArchived
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
      label: wallet.hasTransactions ? <Tooltip title="Нельзя удалить — есть транзакции"><span>Удалить</span></Tooltip> : 'Удалить',
      danger: true,
      disabled: wallet.hasTransactions,
      onClick: () => openModal(WalletDeleteModal, { wallet }),
    },
  ];

  return <ActionsDropdown items={menuItems} />;
};

export default WalletActionsDropdown;
