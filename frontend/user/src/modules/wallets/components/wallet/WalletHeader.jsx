import React from 'react';
import { Space } from 'antd';
import CloseMinimizeBtns from 'src/components/ui/CloseMinimizeBtns';
import WalletActionsDropdown from '../WalletActionsDropdown'
import CommentCell from 'src/features/forms/CommentCell';
import { useWalletMutations } from '../../hooks/useWalletMutations';

const WalletHeader = ({ wallet, onRefresh }) => {
  const { editWallet } = useWalletMutations();

  const handleSaveComment = async (comment) => {
    await editWallet.mutateAsync({ id: wallet.id, name: wallet.name, comment });
  };
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
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)', fontSize: '12px' }}>
                <span>Активов: {wallet.assets.length}</span>
                <CommentCell comment={wallet.comment} onSave={handleSaveComment}/>
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
