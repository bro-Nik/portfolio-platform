import React, { useState } from 'react';
import { Modal } from 'antd';
import { useModalStore } from '@portfolio/shared';
import WatchlistItemForm from '../WatchlistItemForm';

const WatchlistAssetEditModal = () => {
  const { modalProps, closeModal } = useModalStore();
  const { item } = modalProps;
  const [subview, setSubview] = useState(null);

  return (
    <Modal
      title={subview ? null : 'Редактировать запись'}
      open={true}
      onCancel={closeModal}
      closable={!subview}
      footer={null}
      width={500}
      destroyOnHidden
    >
      <WatchlistItemForm
        item={item}
        onSuccess={closeModal}
        onCancel={closeModal}
        onSubviewChange={setSubview}
      />
    </Modal>
  );
};

export default WatchlistAssetEditModal;
