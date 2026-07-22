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
import TagManagementModal from 'src/modules/portfolios/components/modals/TagManagementModal';
import TagAssignPopover from 'src/modules/portfolios/components/TagAssignPopover';
import { getTradingViewUrl } from 'src/utils/format';
import { useWalletMutations } from 'src/modules/wallets/hooks/useWalletMutations';

const AssetActionsDropdown = ({ wallet, asset, btn, onUpdate }) => {
  const { openModal } = useModalStore();
  const { archiveWalletAsset, unarchiveWalletAsset } = useWalletMutations();

  const handleArchive = async () => {
    await archiveWalletAsset.mutateAsync({ walletId: wallet.id, assetId: asset.id });
  };

  const handleUnarchive = async () => {
    await unarchiveWalletAsset.mutateAsync({ walletId: wallet.id, assetId: asset.id });
  };

  const menuItems = [
    {
      key: 'edit',
      icon: <Pencil size={16} />,
      label: 'Редактировать',
      disabled: true,
    },
    {
      key: 'transfer',
      icon: <Pencil size={16} />,
      label: 'Отправить',
      disabled: asset.isArchived,
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
      onClick: () => window.open(getTradingViewUrl(asset.symbol, wallet.market), '_blank', 'noopener,noreferrer'),
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
