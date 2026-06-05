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
import AssetDeleteModal from './modals/AssetDelete';
import TagManagementModal from './modals/TagManagementModal';
import TagAssignPopover from './TagAssignPopover';
import { getTradingViewUrl } from '/app/src/utils/format';


const AssetActionsDropdown = ({ portfolio, asset, btn, onUpdate }) => {
  const { openModal } = useModalStore();
  const entityType = portfolio ? 'portfolio_asset' : 'wallet_asset';

  const menuItems = [
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
      key: 'tradingview',
      icon: <ArrowTopRightOnSquareIcon />,
      label: 'Посмотреть на TradingView',
      onClick: () => window.open(getTradingViewUrl(asset.symbol, asset.tickerId), '_blank', 'noopener,noreferrer'),
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
      onClick: () => openModal(AssetDeleteModal, { portfolio, asset }),
    },
  ];

  return (
    <div className="d-flex align-items-center gap-1">
      <TagAssignPopover entityType={entityType} entityId={asset?.id} assignedTags={asset?.tags} onUpdate={onUpdate} />
      <ActionsDropdown items={menuItems} btn={btn}/>
    </div>
  );
};

export default AssetActionsDropdown;
