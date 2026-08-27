import { ConfirmDeleteModal, useModalStore } from '@portfolio/shared';
import { useTaskActions } from '../hooks/useTaskActions';
import { Task } from '../../../../types/task';

interface TaskDelModalProps { task: Task }

export const TaskDelModal: React.FC<TaskDelModalProps> = ({ task }) => {
  const { closeModal } = useModalStore();
  const { deleteTask } = useTaskActions();

  if (!task) return null;

  return (
    <ConfirmDeleteModal
      title="Удалить задачу?"
      entityName={<strong>{task.name}</strong>}
      onConfirm={() => {
        deleteTask(task.id);
      }}
      onCancel={closeModal}
    />
  );
};
