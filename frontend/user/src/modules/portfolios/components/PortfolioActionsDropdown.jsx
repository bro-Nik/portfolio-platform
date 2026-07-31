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
import PortfolioEditModal from './modals/PortfolioEdit';
import PortfolioDeleteModal from './modals/PortfolioDelete';
import TagManagerSelect from './TagManagerSelect';
import { usePortfolioMutations } from 'src/modules/portfolios/hooks/usePortfolioMutations';

const PortfolioActionsDropdown = ({ portfolio, onUpdate }) => {
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
      label: <TagManagerSelect trigger="menu" entityType="portfolio" entityId={portfolio?.id} assignedTags={portfolio?.tags} />,
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

  return <ActionsDropdown items={menuItems} />;
};

export default PortfolioActionsDropdown;
