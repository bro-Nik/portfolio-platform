import { useModalStore } from '/app/src/stores/modalStore';
import {
  ArchiveBoxXMarkIcon,
  PencilIcon,
  Square2StackIcon,
  TrashIcon,
  ArrowTopRightOnSquareIcon,
  TagIcon,
} from '@heroicons/react/16/solid'
import ActionsDropdown from '/app/src/features/dropdowns/ActionsDropdown';
import WalletEditModal from './modals/WalletEdit';
import WalletDeleteModal from './modals/WalletDelete';
import TagManagementModal from '/app/src/modules/portfolios/components/modals/TagManagementModal';
import TagAssignPopover from '/app/src/modules/portfolios/components/TagAssignPopover';

const WalletActionsDropdown = ({ wallet, btn, onUpdate }) => {
  const { openModal } = useModalStore();

  const menuItems = [
    {
      key: 'edit',
      icon: <PencilIcon />,
      label: 'Редактировать',
      onClick: () => openModal(WalletEditModal, { wallet }),
    },
    {
      key: 'duplicate',
      icon: <Square2StackIcon />,
      label: 'Дублировать',
      disabled: true,
    },
    {
      key: 'export',
      icon: <ArrowTopRightOnSquareIcon />,
      label: 'Экспортировать',
      disabled: true,
    },
    {
      type: 'divider',
    },
    {
      key: 'tags',
      icon: <TagIcon />,
      label: 'Управление тегами',
      onClick: () => openModal(TagManagementModal, { onTagsChange: onUpdate }),
    },
    {
      type: 'divider',
    },
    {
      key: 'archive',
      icon: <ArchiveBoxXMarkIcon />,
      label: 'Архивировать',
      disabled: true,
    },
    {
      key: 'delete',
      icon: <TrashIcon />,
      label: 'Удалить',
      danger: true,
      onClick: () => openModal(WalletDeleteModal, { wallet }),
    },
  ];

  return (
    <div className="d-flex align-items-center gap-1">
      <TagAssignPopover entityType="wallet" entityId={wallet?.id} assignedTags={wallet?.tags} onUpdate={onUpdate} />
      <ActionsDropdown items={menuItems} btn={btn}/>
    </div>
  );
};

export default WalletActionsDropdown;
