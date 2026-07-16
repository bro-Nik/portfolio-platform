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
import TagManagementModal from 'src/modules/portfolios/components/modals/TagManagementModal';
import TagAssignPopover from 'src/modules/portfolios/components/TagAssignPopover';
import { getTradingViewUrl } from 'src/utils/format';

const AssetActionsDropdown = ({ wallet, asset, btn, onUpdate }) => {
  const { openModal } = useModalStore();

  const menuItems = [
    {
      key: 'transfer',
      icon: <Pencil size={16} />,
      label: 'Отправить',
    },
    {
      key: 'edit',
      icon: <Pencil size={16} />,
      label: 'Редактировать',
      disabled: true,
    },
    {
      key: 'duplicate',
      icon: <Copy size={16} />,
      label: 'Переместить',
      disabled: true,
    },
    {
      key: 'export',
      icon: <ExternalLink size={16} />,
      label: 'Экспортировать',
      disabled: true,
    },
    {
      key: 'tradingview',
      icon: <ExternalLink size={16} />,
      label: 'Посмотреть на TradingView',
      onClick: () => window.open(getTradingViewUrl(asset.symbol, asset.tickerId), '_blank', 'noopener,noreferrer'),
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
    },
  ];

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
      <TagAssignPopover entityType="wallet_asset" entityId={asset?.id} assignedTags={asset?.tags} onUpdate={onUpdate} />
      <ActionsDropdown items={menuItems} btn={btn}/>
    </div>
  );
};

export default AssetActionsDropdown;
