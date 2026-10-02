import { useModalStore } from '@portfolio/shared';
import { Inbox, Undo2, Pencil, Trash2 } from 'lucide-react';
import ActionsDropdown from 'src/features/dropdowns/ActionsDropdown';
import WatchlistAssetEditModal from './modals/WishlistAssetEdit';
import WatchlistAssetDeleteModal from './modals/WishlistAssetDelete';
import { useWatchlistOperations } from '../hooks/useWatchlistOperations';

const WatchlistAssetActionsDropdown = ({ item }) => {
  const { openModal } = useModalStore();
  const { archiveItem } = useWatchlistOperations();

  // Optimistic temp-строка ещё не подтверждена сервером — действий нет.
  if (typeof item.id !== 'number') return null;

  const menuItems = [
    {
      key: 'edit',
      icon: <Pencil size={16} />,
      label: 'Редактировать',
      disabled: item.isArchived,
      onClick: () => openModal(WatchlistAssetEditModal, { item }),
    },
    {
      type: 'divider',
    },
    ...(item.isArchived
      ? [{
          key: 'unarchive',
          icon: <Undo2 size={16} />,
          label: 'Разархивировать',
          onClick: () => archiveItem(item.id, false),
        }]
      : [{
          key: 'archive',
          icon: <Inbox size={16} />,
          label: 'Архивировать',
          onClick: () => archiveItem(item.id, true),
        }]
    ),
    {
      key: 'delete',
      icon: <Trash2 size={16} />,
      label: 'Удалить',
      danger: true,
      onClick: () => openModal(WatchlistAssetDeleteModal, { item }),
    },
  ];

  return <ActionsDropdown items={menuItems} />;
};

export default WatchlistAssetActionsDropdown;
