import { useModalStore } from '/app/src/stores/modalStore';
import {
  ArchiveBoxXMarkIcon,
  PencilIcon,
  Square2StackIcon,
  TrashIcon,
  ArrowTopRightOnSquareIcon,
} from '@heroicons/react/16/solid'
import ActionsDropdown from '/app/src/features/dropdowns/ActionsDropdown';
import PortfolioEditModal from './modals/PortfolioEdit';
import PortfolioDeleteModal from './modals/PortfolioDelete';

const PortfolioActionsDropdown = ({ portfolio, btn }) => {
  const { openModal } = useModalStore();

  const menuItems = [
    {
      key: 'edit',
      icon: <PencilIcon />,
      label: 'Редактировать',
      onClick: () => openModal(PortfolioEditModal, { portfolio: portfolio }),
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
      onClick: () => openModal(PortfolioDeleteModal, { portfolio: portfolio }),
    },
  ];

  return <ActionsDropdown items={menuItems} btn={btn}/>;
};

export default PortfolioActionsDropdown;
