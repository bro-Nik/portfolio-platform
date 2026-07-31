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
import TagManagerSelect from 'src/modules/portfolios/components/TagManagerSelect';
import { getTradingViewUrl } from 'src/utils/format';
import { useWalletMutations } from 'src/modules/wallets/hooks/useWalletMutations';

const AssetActionsDropdown = ({ wallet, asset, onUpdate }) => {
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
      label: <TagManagerSelect trigger="menu" entityType="wallet_asset" entityId={asset?.id} assignedTags={asset?.tags} />,
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

  return <ActionsDropdown items={menuItems} />;
};

export default AssetActionsDropdown;
