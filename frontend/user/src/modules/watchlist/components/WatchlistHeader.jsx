import React from 'react';
import { Button } from 'antd';
import { useModalStore } from '@portfolio/shared';
import WatchlistAssetAddModal from './modals/WishlistAssetAdd';

const WatchlistHeader = () => {
  const { openModal } = useModalStore();

  return (
    <div style={{ marginBottom: 48 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        <div style={{ flex: '0 0 auto' }}>
          <h1>Избранное</h1>
        </div>
        <div style={{ flex: '0 0 auto', marginLeft: 'auto' }}>
          <Button type="primary" onClick={() => openModal(WatchlistAssetAddModal)}>
            Добавить актив
          </Button>
        </div>
      </div>
    </div>
  );
};

export default WatchlistHeader;
