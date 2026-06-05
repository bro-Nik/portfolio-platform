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
import TagManagementModal from '/app/src/modules/portfolios/components/modals/TagManagementModal';
import TagAssignPopover from '/app/src/modules/portfolios/components/TagAssignPopover';

const AssetActionsDropdown = ({ wallet, asset, btn, onUpdate }) => {
  const { openModal } = useModalStore();

  const menuItems = [
    {
      key: 'transfer',
      icon: <PencilIcon />,
      label: 'Отправить',
    },
    {
      key: 'edit',
      icon: <PencilIcon />,
      label: 'Редактировать',
      disabled: true,
    },
    {
      key: 'duplicate',
      icon: <Square2StackIcon />,
      label: 'Переместить',
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
      // onClick: () => openModal(AssetDeleteModal, { portfolio, asset }),
    },
  ];

  return (
    <div className="d-flex align-items-center gap-1">
      <TagAssignPopover entityType="wallet_asset" entityId={asset?.id} assignedTags={asset?.tags} onUpdate={onUpdate} />
      <ActionsDropdown items={menuItems} btn={btn}/>
    </div>
  );
};

export default AssetActionsDropdown;
