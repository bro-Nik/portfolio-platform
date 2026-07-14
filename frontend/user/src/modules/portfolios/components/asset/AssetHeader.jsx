import React from 'react';
import { Space, Button } from 'antd';
import { ExternalLink } from 'lucide-react';
import { formatCurrency, getTradingViewUrl } from '/app/src/utils/format';
import { useModalStore } from '/app/src/stores/modalStore';
import CloseMinimizeBtns from '/app/src/components/ui/CloseMinimizeBtns';
import AssetActionsDropdown from '../AssetActionsDropdown';
import TransactionEditModal from '/app/src/modules/transaction/modals/TransactionEdit';

const AssetHeader = ({ portfolio, asset }) => {
  const { openModal } = useModalStore();
  return (
    <div className="asset-header" style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: '1rem', color: 'rgba(0,0,0,0.45)', margin: 0 }}>
                {asset.name} 
                <span style={{ textTransform: 'uppercase' }}>({asset.symbol})</span>
                <a href={getTradingViewUrl(asset.symbol, asset.tickerId)} target="_blank" rel="noopener noreferrer" style={{ marginLeft: 4 }} onClick={(e) => e.stopPropagation()}>
                  <ExternalLink size={14} />
                </a>
              </h1>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <img className="img-asset" src={asset.image?.replace('/24/', '/40/')} alt={`${asset.name} logo`} />
                <span style={{ fontSize: '2.5rem', fontWeight: 600 }}>{formatCurrency(asset.price)}</span>
              </div>

              <div style={{ color: 'rgba(0,0,0,0.45)', fontSize: '12px' }}>
                <span style={{ marginRight: 12 }}>Портфель: {portfolio.name}</span>
                <span style={{ textTransform: 'capitalize' }}>Рынок: {portfolio.market}</span>
              </div>
            </div>
          </div>
        </div>

        <div style={{ flex: '0 0 auto', marginLeft: 'auto' }}>
          <Space>
            <Button type="primary"  onClick={() => openModal(TransactionEditModal, { tickerId: asset.tickerId, portfolioId: portfolio.id })} >
              Добавить транзакцию
            </Button>
            <AssetActionsDropdown portfolio={portfolio} asset={asset} btn='btn' />
          </Space>
        </div>
      </div>
      <CloseMinimizeBtns id={asset.id} type='portfolio_asset' parentId={portfolio.id} />
    </div>
  );
};

export default AssetHeader;
