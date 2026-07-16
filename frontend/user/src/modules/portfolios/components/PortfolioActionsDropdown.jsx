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
import PortfolioEditModal from './modals/PortfolioEdit';
import PortfolioDeleteModal from './modals/PortfolioDelete';
import TagManagementModal from './modals/TagManagementModal';
import TagAssignPopover from './TagAssignPopover';

const PortfolioActionsDropdown = ({ portfolio, btn, onUpdate }) => {
  const { openModal } = useModalStore();

  const menuItems = [
    {
      key: 'edit',
      icon: <Pencil size={16} />,
      label: 'Редактировать',
      onClick: () => openModal(PortfolioEditModal, { portfolio: portfolio }),
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
      onClick: () => openModal(PortfolioDeleteModal, { portfolio: portfolio }),
    },
  ];

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
      <TagAssignPopover entityType="portfolio" entityId={portfolio?.id} assignedTags={portfolio?.tags} onUpdate={onUpdate} />
      <ActionsDropdown items={menuItems} btn={btn}/>
    </div>
  );
};

export default PortfolioActionsDropdown;
