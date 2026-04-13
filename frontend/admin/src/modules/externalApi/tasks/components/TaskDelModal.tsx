import { Modal } from 'antd';
import { useModalStore } from '@shared';
import { useTaskActions } from '../hooks/useTaskActions';
import { Task } from '/app/src/types/task';

interface TaskDelModalProps { task: Task }

export const TaskDelModal: React.FC<TaskDelModalProps> = ({ task }) => {
  const { closeModal } = useModalStore();
  const { deleteTask, isDeleting } = useTaskActions();

  if (!task) return null;

  const handleConfirm = async () => {
    deleteTask(task.id);
    closeModal();
  };

  return (
    <Modal
      title="Удалить задачу?"
      open={true}
      onOk={handleConfirm}
      onCancel={closeModal}
      okText="Удалить"
      cancelText="Отмена"
      okType="danger"
      centered
      confirmLoading={isDeleting}
    >
      <p>Вы уверены, что хотите удалить <strong>{task.name}</strong>?</p>
      <p style={{ color: '#ff4d4f', fontSize: '12px' }}>
        Это действие нельзя отменить.
      </p>
    </Modal>
  );
};
