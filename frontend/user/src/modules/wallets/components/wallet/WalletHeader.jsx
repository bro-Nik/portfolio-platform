import React from 'react';
import { Space } from 'antd';
import CloseMinimizeBtns from 'src/components/ui/CloseMinimizeBtns';
import WalletActionsDropdown from '../WalletActionsDropdown'

const WalletHeader = ({ wallet, onRefresh }) => {
  return (
    <div className="portfolio-header" style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: '1.75rem', marginBottom: 4 }}>
                {wallet.name}
                {wallet.isArchived && <span style={{ color: 'var(--text-muted)', fontSize: 10, marginLeft: 8 }}>Архивный</span>}
              </h1>
              <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                <span>Активов: {wallet.assets.length}</span>
              </div>
            </div>
          </div>
        </div>

        <div style={{ flex: '0 0 auto', marginLeft: 'auto' }}>
          <Space>
            <WalletActionsDropdown wallet={wallet} onUpdate={onRefresh} />
          </Space>
        </div>

      </div>
      <CloseMinimizeBtns id={wallet.id} type='wallet' />
    </div>
  );
};

export default WalletHeader;
