import { useModalStore } from '@portfolio/shared';
import { TaskDelModal } from '../components/TaskDelModal';
import { TaskDetailsModal } from '../components/TaskDetailsModal';
import { TaskFormModal } from '../components/TaskFormModal';
import { Task } from '../../../../types/task';

export const useTaskModals = () => {
  const { openModal } = useModalStore();

  return {
    taskDetailsModal: (task: Task) => openModal(TaskDetailsModal, { task }),
    taskFormModal: (task?: Task) => openModal(TaskFormModal, { task }),
    taskDeleteConfirmModal: (task: Task) => openModal(TaskDelModal, { task }),
  };
};
