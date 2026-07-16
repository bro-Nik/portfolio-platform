import React from 'react';
import { Button, Space } from 'antd';
import { useModalStore } from '@portfolio/shared';
import CloseMinimizeBtns from 'src/components/ui/CloseMinimizeBtns';
import AssetAddModal from '../modals/AssetAdd';
import PortfolioActionsDropdown from '../PortfolioActionsDropdown'

const PortfolioHeader = ({ portfolio, onRefresh }) => {
  const { openModal } = useModalStore();

  return (
    <div className="portfolio-header" style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: '1.75rem', marginBottom: 4 }}>{portfolio.name}</h1>
              <div style={{ color: 'rgba(0,0,0,0.45)', fontSize: '12px' }}>
                <span style={{ marginRight: 12 }}>Рынок: {portfolio.market}</span>
                <span>Активов: {portfolio.assets.length}</span>
              </div>
            </div>
          </div>
        </div>

        <div style={{ flex: '0 0 auto', marginLeft: 'auto' }}>
          <Space>
            <Button type="primary"  onClick={() => openModal(AssetAddModal, { portfolio: portfolio })} >
              Добавить актив
            </Button>
            <PortfolioActionsDropdown portfolio={portfolio} btn='btn' onUpdate={onRefresh} />
          </Space>
        </div>
      </div>
      <CloseMinimizeBtns id={portfolio.id} type='portfolio' />
    </div>
  );
};

export default PortfolioHeader;
