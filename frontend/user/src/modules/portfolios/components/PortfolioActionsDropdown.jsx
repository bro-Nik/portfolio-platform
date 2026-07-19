import { useModalStore } from '@portfolio/shared';
import { Tooltip } from 'antd';
import {
  Inbox,
  Undo2,
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
import { usePortfolioMutations } from 'src/modules/portfolios/hooks/usePortfolioMutations';

const PortfolioActionsDropdown = ({ portfolio, btn, onUpdate }) => {
  const { openModal } = useModalStore();
  const { archivePortfolio, unarchivePortfolio } = usePortfolioMutations();

  const handleArchive = async () => {
    await archivePortfolio.mutateAsync(portfolio.id);
  };

  const handleUnarchive = async () => {
    await unarchivePortfolio.mutateAsync(portfolio.id);
  };

  const menuItems = [
    {
      key: 'edit',
      icon: <Pencil size={16} />,
      label: 'Редактировать',
      disabled: portfolio.isArchived,
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
    ...(portfolio.isArchived
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
      label: portfolio.hasTransactions ? <Tooltip title="Нельзя удалить — есть транзакции"><span>Удалить</span></Tooltip> : 'Удалить',
      danger: true,
      disabled: portfolio.hasTransactions,
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
