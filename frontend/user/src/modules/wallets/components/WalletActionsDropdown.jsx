import { useModalStore } from '/app/src/stores/modalStore';
import {
  ArchiveBoxXMarkIcon,
  PencilIcon,
  Square2StackIcon,
  TrashIcon,
  ArrowTopRightOnSquareIcon,
} from '@heroicons/react/16/solid'
import ActionsDropdown from '/app/src/features/dropdowns/ActionsDropdown';
import WalletEditModal from './modals/WalletEdit';
import WalletDeleteModal from './modals/WalletDelete';

const WalletActionsDropdown = ({ wallet, btn }) => {
  const { openModal } = useModalStore();

  const menuItems = [
    {
      key: 'edit',
      icon: <PencilIcon />,
      label: 'Редактировать',
      onClick: () => openModal(WalletEditModal, { wallet }),
    },
    {
      key: 'duplicate',
      icon: <Square2StackIcon />,
      label: 'Дублировать',
      disabled: true,
    },
    {
      key: 'export',
      icon: <ArrowTopRightOnSquareIcon />,
      label: 'Экспортировать',
      disabled: true,
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
      onClick: () => openModal(WalletDeleteModal, { wallet }),
    },
  ];

  return <ActionsDropdown items={menuItems} btn={btn}/>;
};

export default WalletActionsDropdown;
