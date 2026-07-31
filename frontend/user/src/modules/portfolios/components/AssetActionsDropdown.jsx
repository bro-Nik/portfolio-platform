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
import AssetDeleteModal from './modals/AssetDelete';
import TagManagerSelect from 'src/modules/tags/components/TagManagerSelect';
import { getTradingViewUrl } from 'src/utils/format';
import { usePortfolioMutations } from 'src/modules/portfolios/hooks/usePortfolioMutations';


const AssetActionsDropdown = ({ portfolio, asset, onUpdate }) => {
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
      label: <TagManagerSelect trigger="menu" entityType={entityType} entityId={asset?.id} assignedTags={asset?.tags} parentId={portfolio?.id} />,
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

  return <ActionsDropdown items={menuItems} />;
};

export default AssetActionsDropdown;
