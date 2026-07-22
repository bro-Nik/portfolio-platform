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
import AssetDeleteModal from './modals/AssetDelete';
import TagManagementModal from './modals/TagManagementModal';
import TagAssignPopover from './TagAssignPopover';
import { getTradingViewUrl } from 'src/utils/format';
import { usePortfolioMutations } from 'src/modules/portfolios/hooks/usePortfolioMutations';


const AssetActionsDropdown = ({ portfolio, asset, btn, onUpdate }) => {
  const { openModal } = useModalStore();
  const { archiveAsset, unarchiveAsset } = usePortfolioMutations();
  const entityType = portfolio ? 'portfolio_asset' : 'wallet_asset';

  const handleArchive = async () => {
    await archiveAsset.mutateAsync({ portfolioId: portfolio.id, assetId: asset.id });
  };

  const handleUnarchive = async () => {
    await unarchiveAsset.mutateAsync({ portfolioId: portfolio.id, assetId: asset.id });
  };

  const menuItems = [
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
      onClick: () => window.open(getTradingViewUrl(asset.symbol, portfolio.market), '_blank', 'noopener,noreferrer'),
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
      onClick: () => openModal(AssetDeleteModal, { portfolio, asset }),
    },
  ];

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
      <TagAssignPopover entityType={entityType} entityId={asset?.id} assignedTags={asset?.tags} onUpdate={onUpdate} />
      <ActionsDropdown items={menuItems} btn={btn}/>
    </div>
  );
};

export default AssetActionsDropdown;
