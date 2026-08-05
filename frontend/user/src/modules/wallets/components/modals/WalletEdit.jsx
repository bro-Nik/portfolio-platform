import React, { useState } from 'react';
import { Modal } from 'antd';
import { useModalStore } from '@portfolio/shared';
import WalletForm from '../WalletForm';

const WalletEditModal = () => {
  const { modalProps, closeModal } = useModalStore();
  const {
    wallet = null,
    title = wallet ? 'Редактировать кошелек' : 'Добавить кошелек'
  } = modalProps;
  const [subview, setSubview] = useState(null);

  return (
    <Modal
      title={subview ? null : title}
      open={true}
      onCancel={closeModal}
      closable={!subview}
      footer={null}
      width={500}
      destroyOnHidden
    >
      <WalletForm
        wallet={wallet}
        onSuccess={closeModal}
        onCancel={closeModal}
        onSubviewChange={setSubview}
      />
    </Modal>
  );
};

export default WalletEditModal;
