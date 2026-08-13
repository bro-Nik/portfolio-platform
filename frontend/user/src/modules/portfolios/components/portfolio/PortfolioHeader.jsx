import React from 'react';
import { Button, Space } from 'antd';
import { useModalStore } from '@portfolio/shared';
import CloseMinimizeBtns from 'src/components/ui/CloseMinimizeBtns';
import AssetAddModal from '../modals/AssetAdd';
import PortfolioActionsDropdown from '../PortfolioActionsDropdown'
import CommentCell from 'src/features/forms/CommentCell';
import { usePortfolioMutations } from '../../hooks/usePortfolioMutations';

const PortfolioHeader = ({ portfolio, onRefresh }) => {
  const { openModal } = useModalStore();
  const { editPortfolio } = usePortfolioMutations();

  const handleSaveComment = async (comment) => {
    await editPortfolio.mutateAsync({ id: portfolio.id, name: portfolio.name, market: portfolio.market, comment });
  };

  return (
    <div className="portfolio-header" style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: '1.75rem', marginBottom: 4 }}>
                {portfolio.name}
                {portfolio.isArchived && <span style={{ color: 'var(--text-muted)', fontSize: 10, marginLeft: 8 }}>Архивный</span>}
              </h1>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)', fontSize: '12px' }}>
                <span style={{ textTransform: 'capitalize' }}>Рынок: {portfolio.market}</span>
                <span>Активов: {portfolio.assets.length}</span>
                <CommentCell comment={portfolio.comment} onSave={handleSaveComment}/>
              </div>
            </div>
          </div>
        </div>

        <div style={{ flex: '0 0 auto', marginLeft: 'auto' }}>
          <Space>
            <Button type="primary" disabled={portfolio.isArchived} onClick={() => openModal(AssetAddModal, { portfolio: portfolio })} >
              Добавить актив
            </Button>
            <PortfolioActionsDropdown portfolio={portfolio} onUpdate={onRefresh} />
          </Space>
        </div>
      </div>
      <CloseMinimizeBtns id={portfolio.id} type='portfolio' />
    </div>
  );
};

export default PortfolioHeader;
