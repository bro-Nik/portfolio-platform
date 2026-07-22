import { Modal } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { useProviderActions } from '../hooks/useProviderActions';
import { Provider } from '../../../../types/provider';

interface ProviderDelModalProps { provider: Provider }

export const ProviderDelModal: React.FC = () => {
  const { modalProps, closeModal } = useModalStore();
  const { provider }: ProviderDelModalProps = modalProps;
  const { deleteProvider, isDeleting } = useProviderActions();

  if (!provider) return null;

  const handleConfirm = async () => {
    deleteProvider(provider.name);
    closeModal();
  };

  return (
    <Modal
      title="Сбросить конфиг провайдера?"
      open={true}
      onOk={handleConfirm}
      onCancel={closeModal}
      okText="Сбросить"
      cancelText="Отмена"
      okType="danger"
      confirmLoading={isDeleting}
    >
      {(
        <>
          <p>Будут удалены настройки провайдера <strong>{provider.name}</strong>:</p>
          <ul>
            <li>API ключ</li>
            <li>кастомные лимиты запросов</li>
            <li>задержка повтора и таймаут</li>
          </ul>
          <p style={{ color: '#52c41a', fontSize: '13px' }}>
            Провайдер останется доступен с настройками по умолчанию.
          </p>
        </>
      )}
    </Modal>
  );
};
