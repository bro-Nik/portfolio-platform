import { useState } from 'react';
import { Modal } from 'antd';
import { useNotifications } from '../hooks/useNotifications.js';

export interface DeleteResult {
  success: boolean;
  error?: string;
}

export interface ConfirmDeleteModalProps {
  entityName?: React.ReactNode;
  question?: React.ReactNode;
  questionPrefix?: string;
  title?: string;
  okText?: string;
  cancelText?: string;
  extraNote?: React.ReactNode;
  successMessage?: string;
  fallbackErrorMessage?: string;
  onConfirm: () => Promise<DeleteResult | void> | DeleteResult | void;
  onCancel: () => void;
}

export const ConfirmDeleteModal = ({
  entityName,
  question,
  questionPrefix = 'Вы уверены, что хотите удалить',
  title = 'Подтверждение удаления',
  okText = 'Удалить',
  cancelText = 'Отмена',
  extraNote,
  successMessage,
  fallbackErrorMessage,
  onConfirm,
  onCancel,
}: ConfirmDeleteModalProps) => {
  const { success, error } = useNotifications();
  const [submitting, setSubmitting] = useState(false);

  const handleOk = async () => {
    setSubmitting(true);
    try {
      const result = await onConfirm();
      if (!result || result.success) {
        if (successMessage) success(successMessage);
      } else {
        error(result.error || fallbackErrorMessage || 'Произошла ошибка');
      }
      onCancel();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title={title}
      open={true}
      onOk={handleOk}
      onCancel={onCancel}
      okText={okText}
      cancelText={cancelText}
      okType="danger"
      confirmLoading={submitting}
    >
      <p>{question ?? <>{questionPrefix} &quot;{entityName}&quot;?</>}</p>
      <p style={{ color: '#ff4d4f', fontSize: '12px' }}>
        Это действие нельзя отменить.
      </p>
      {extraNote}
    </Modal>
  );
};
