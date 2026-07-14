import React from 'react';
import { Button } from 'antd';
import { useModalStore } from '/app/src/stores/modalStore';
import WalletEditModal from '../modals/WalletEdit';

const WalletsHeader = () => {
  const { openModal } = useModalStore();

  return (
    <div style={{ marginBottom: 48 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        <div style={{ flex: '0 0 auto' }}>
          <h1>Кошельки</h1>
        </div>
        <div style={{ flex: '0 0 auto', marginLeft: 'auto' }}>
          <Button type="primary" onClick={() => openModal(WalletEditModal)}>
            Добавить кошелек
          </Button>
        </div>
      </div>
    </div>
  );
};

export default WalletsHeader;
