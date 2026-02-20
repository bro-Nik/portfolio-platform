import React from 'react';
import { Button, Space } from 'antd';
import { useModalStore } from '/app/src/stores/modalStore';
import CloseMinimizeBtns from '/app/src/components/ui/CloseMinimizeBtns';
import AssetAddModal from '../modals/AssetAdd';
import PortfolioActionsDropdown from '../PortfolioActionsDropdown'

const PortfolioHeader = ({ portfolio }) => {
  const { openModal } = useModalStore();

  return (
    <div className="portfolio-header mb-4">
      <div className="row align-items-center">
        <div className="col">
          <div className="d-flex align-items-center">
            <div>
              <h1 className="h3 mb-1">{portfolio.name}</h1>
              <div className="text-muted small">
                <span className="me-3">Рынок: {portfolio.market}</span>
                <span>Активов: {portfolio.assets.length}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="col-auto ms-auto">
          <Space>
            <Button type="primary"  onClick={() => openModal(AssetAddModal, { portfolio: portfolio })} >
              Добавить актив
            </Button>
            <PortfolioActionsDropdown portfolio={portfolio} btn='btn' />
          </Space>

        </div>

      </div>
      <CloseMinimizeBtns id={portfolio.id} type='portfolio' />
    </div>
  );
};

export default PortfolioHeader;
