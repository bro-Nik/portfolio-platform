import { useModalStore } from '@portfolio/shared';
import {
  Inbox,
  Pencil,
  Copy,
  Trash2,
  ExternalLink,
  Tag,
} from 'lucide-react'
import ActionsDropdown from 'src/features/dropdowns/ActionsDropdown';
import WalletEditModal from './modals/WalletEdit';
import WalletDeleteModal from './modals/WalletDelete';
import TagManagementModal from 'src/modules/portfolios/components/modals/TagManagementModal';
import TagAssignPopover from 'src/modules/portfolios/components/TagAssignPopover';

const WalletActionsDropdown = ({ wallet, btn, onUpdate }) => {
  const { openModal } = useModalStore();

  const menuItems = [
    {
      key: 'edit',
      icon: <Pencil size={16} />,
      label: 'Редактировать',
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
      icon: <Tag size={16} />,
      label: 'Управление тегами',
      onClick: () => openModal(TagManagementModal, { onTagsChange: onUpdate }),
    },
    {
      type: 'divider',
    },
    {
      key: 'archive',
      icon: <Inbox size={16} />,
      label: 'Архивировать',
      disabled: true,
    },
    {
      key: 'delete',
      icon: <Trash2 size={16} />,
      label: 'Удалить',
      danger: true,
      onClick: () => openModal(WalletDeleteModal, { wallet }),
    },
  ];

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
      <TagAssignPopover entityType="wallet" entityId={wallet?.id} assignedTags={wallet?.tags} onUpdate={onUpdate} />
      <ActionsDropdown items={menuItems} btn={btn}/>
    </div>
  );
};

export default WalletActionsDropdown;
