import { useModalStore } from '/app/src/stores/modalStore';
import { Pencil, Trash2 } from 'lucide-react'
import ActionsDropdown from '/app/src/features/dropdowns/ActionsDropdown';
import TransactionEditModal from '/app/src/modules/transaction/modals/TransactionEdit';
import TransactionDeleteModal from '/app/src/modules/transaction/modals/TransactionDelete';

const TransactionActionsDropdown = ({ portfolio, wallet, asset, transaction, btn }) => {
  const { openModal } = useModalStore();

  const menuItems = [
    {
      key: 'edit',
      icon: <Pencil size={16} />,
      label: 'Редактировать',
      onClick: () => openModal(TransactionEditModal, { tickerId: asset.tickerId, portfolioId: portfolio.id, transaction }),
    },
    {
      type: 'divider',
    },
    {
      key: 'delete',
      icon: <Trash2 size={16} />,
      label: 'Удалить',
      danger: true,
      onClick: () => openModal(TransactionDeleteModal, { transaction }),
    },
  ];

  return <ActionsDropdown items={menuItems} btn={btn}/>;
};

export default TransactionActionsDropdown;
