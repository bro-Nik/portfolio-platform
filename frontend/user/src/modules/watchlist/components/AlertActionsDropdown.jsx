import { useModalStore } from '@portfolio/shared';
import { Pencil, Power, PowerOff, Trash2 } from 'lucide-react';
import ActionsDropdown from 'src/features/dropdowns/ActionsDropdown';
import AlertEditModal from './modals/AlertEdit';
import AlertDeleteModal from './modals/AlertDelete';
import { useWatchlistOperations } from '../hooks/useWatchlistOperations';
import { isTriggered } from '../utils/alerts';

const AlertActionsDropdown = ({ item, alert }) => {
  const { openModal } = useModalStore();
  const { toggleAlert } = useWatchlistOperations();
  const triggered = isTriggered(alert);
  const isTemp = typeof alert.id !== 'number';

  const menuItems = [
    {
      key: 'toggle',
      icon: alert.isActive ? <PowerOff size={16} /> : <Power size={16} />,
      label: alert.isActive ? 'Выключить' : 'Включить',
      disabled: triggered || isTemp,
      onClick: () => toggleAlert(alert.id, !alert.isActive),
    },
    {
      key: 'edit',
      icon: <Pencil size={16} />,
      label: 'Редактировать',
      disabled: triggered || isTemp,
      onClick: () => openModal(AlertEditModal, { item, alert }),
    },
    {
      type: 'divider',
    },
    {
      key: 'delete',
      icon: <Trash2 size={16} />,
      label: 'Удалить',
      danger: true,
      disabled: isTemp,
      onClick: () => openModal(AlertDeleteModal, { alert }),
    },
  ];

  return <ActionsDropdown items={menuItems} />;
};

export default AlertActionsDropdown;
