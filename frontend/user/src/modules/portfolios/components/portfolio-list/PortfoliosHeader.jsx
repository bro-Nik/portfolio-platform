import React from 'react';
import { Button } from 'antd';
import { useModalStore } from '/app/src/stores/modalStore';
import PortfolioEditModal from '../modals/PortfolioEdit';

const PortfoliosHeader = () => {
  const { openModal } = useModalStore();

  return (
    <div style={{ marginBottom: 48 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        <div style={{ flex: '0 0 auto' }}>
          <h1>Портфели</h1>
        </div>
        <div style={{ flex: '0 0 auto', marginLeft: 'auto' }}>
          <Button type="primary" onClick={() => openModal(PortfolioEditModal)}>
            Добавить портфель
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PortfoliosHeader;
