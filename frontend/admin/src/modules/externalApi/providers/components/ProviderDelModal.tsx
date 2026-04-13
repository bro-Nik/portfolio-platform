import { Modal } from 'antd';
import { useModalStore } from '@shared';
import { useProviderActions } from '../hooks/useProviderActions';
import { Provider } from '/app/src/types/provider';

interface ProviderDelModalProps { provider: Provider }

export const ProviderDelModal: React.FC<ProviderDelModalProps> = ({ provider }) => {
  const { closeModal } = useModalStore();
  const { deleteProvider, isDeleting } = useProviderActions();

  if (!provider) return null;

  const handleConfirm = async () => {
    deleteProvider(provider.id);
    closeModal();
  };

  return (
    <Modal
      title="Удалить API провайдера?"
      open={true}
      onOk={handleConfirm}
      onCancel={closeModal}
      okText="Удалить"
      cancelText="Отмена"
      okType="danger"
      centered
      confirmLoading={isDeleting}
    >
      <p>Вы уверены, что хотите удалить <strong>{provider.name}</strong>?</p>
      <p style={{ color: '#ff4d4f', fontSize: '12px' }}>
        Это действие нельзя отменить.
      </p>
    </Modal>
  );
};
