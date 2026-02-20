import { useModalStore } from '/app/src/stores/modalStore';
import {
  ArchiveBoxXMarkIcon,
  PencilIcon,
  Square2StackIcon,
  TrashIcon,
  ArrowTopRightOnSquareIcon,
} from '@heroicons/react/16/solid'
import ActionsDropdown from '/app/src/features/dropdowns/ActionsDropdown';
import TransactionEditModal from '/app/src/modules/transaction/modals/TransactionEdit';
import TransactionDeleteModal from '/app/src/modules/transaction/modals/TransactionDelete';

const TransactionActionsDropdown = ({ portfolio, wallet, asset, transaction, btn }) => {
  const { openModal } = useModalStore();

  const menuItems = [
    {
      key: 'edit',
      icon: <PencilIcon />,
      label: 'Редактировать',
      onClick: () => openModal(TransactionEditModal, { tickerId: asset.tickerId, portfolioId: portfolio.id, transaction }),
    },
    {
      type: 'divider',
    },
    {
      key: 'delete',
      icon: <TrashIcon />,
      label: 'Удалить',
      danger: true,
      onClick: () => openModal(TransactionDeleteModal, { transaction }),
    },
  ];

  return <ActionsDropdown items={menuItems} btn={btn}/>;
};

export default TransactionActionsDropdown;
