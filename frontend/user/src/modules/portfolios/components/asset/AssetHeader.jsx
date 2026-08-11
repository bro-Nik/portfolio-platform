import React from 'react';
import { Space, Button } from 'antd';
import { ExternalLink } from 'lucide-react';
import TickerAvatar from 'src/components/TickerAvatar';
import { formatCurrencyFromUsd, getTradingViewUrl } from 'src/utils/format';
import { useDisplayCurrency } from 'src/utils/currency';
import { useModalStore } from '@portfolio/shared';
import CloseMinimizeBtns from 'src/components/ui/CloseMinimizeBtns';
import AssetActionsDropdown from '../AssetActionsDropdown';
import TransactionEditModal from 'src/modules/transaction/modals/TransactionEdit';

const AssetHeader = ({ portfolio, asset }) => {
  useDisplayCurrency();
  const { openModal } = useModalStore();
  return (
    <div className="asset-header" style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: '1rem', color: 'var(--text-muted)', margin: 0 }}>
                {asset.name} 
                <span style={{ textTransform: 'uppercase' }}>({asset.symbol})</span>
                <a href={getTradingViewUrl(asset.symbol, portfolio.market)} target="_blank" rel="noopener noreferrer" style={{ marginLeft: 4 }} onClick={(e) => e.stopPropagation()}>
                  <ExternalLink size={14} />
                </a>
              </h1>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <TickerAvatar src={asset.image?.replace('/24/', '/40/')} symbol={asset.symbol} size={40} />
                <span style={{ fontSize: '2.5rem', fontWeight: 600 }}>{formatCurrencyFromUsd(asset.price, true)}</span>
              </div>

              <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                <span style={{ marginRight: 12 }}>Портфель: {portfolio.name}</span>
                <span style={{ textTransform: 'capitalize' }}>Рынок: {portfolio.market}</span>
              </div>
            </div>
          </div>
        </div>

        <div style={{ flex: '0 0 auto', marginLeft: 'auto' }}>
          <Space>
            <Button type="primary" disabled={asset.isArchived} onClick={() => openModal(TransactionEditModal, { tickerId: asset.tickerId, portfolioId: portfolio.id })} >
              Добавить транзакцию
            </Button>
            <AssetActionsDropdown portfolio={portfolio} asset={asset} />
          </Space>
        </div>
      </div>
      <CloseMinimizeBtns id={asset.id} type='portfolio_asset' parentId={portfolio.id} />
    </div>
  );
};

export default AssetHeader;
