import React from 'react';
import { Space, Button } from 'antd';
import { ExternalLink } from 'lucide-react';
import TickerAvatar from 'src/components/TickerAvatar';
import { formatCurrencyFromUsd, getTradingViewUrl } from 'src/utils/format';
import { useDisplayCurrency } from 'src/utils/currency';
import { useModalStore } from '@portfolio/shared';
import CloseMinimizeBtns from 'src/components/ui/CloseMinimizeBtns';
import WatchlistAssetActionsDropdown from './WishlistAssetActionsDropdown';
import AlertEditModal from './modals/AlertEdit';

const WatchlistItemHeader = ({ item }) => {
  useDisplayCurrency();
  const { openModal } = useModalStore();
  return (
    <div className="asset-header" style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: '1rem', color: 'var(--text-muted)', margin: 0 }}>
                {item.name}
                <span style={{ textTransform: 'uppercase' }}>({item.symbol})</span>
                <a href={getTradingViewUrl(item.symbol, item.market)} target="_blank" rel="noopener noreferrer" style={{ marginLeft: 4 }} onClick={(e) => e.stopPropagation()}>
                  <ExternalLink size={14} />
                </a>
              </h1>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <TickerAvatar src={item.image?.replace('/24/', '/40/')} symbol={item.symbol} size={40} />
                <span style={{ fontSize: '2.5rem', fontWeight: 600 }}>{formatCurrencyFromUsd(item.price, true)}</span>
              </div>

              <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                <span style={{ textTransform: 'capitalize' }}>Рынок: {item.market}</span>
              </div>
            </div>
          </div>
        </div>

        <div style={{ flex: '0 0 auto', marginLeft: 'auto' }}>
          <Space>
            <Button type="primary" disabled={item.isArchived} onClick={() => openModal(AlertEditModal, { item })} >
              Добавить уведомление
            </Button>
            <WatchlistAssetActionsDropdown item={item} />
          </Space>
        </div>
      </div>
      <CloseMinimizeBtns id={item.id} type="wishlist_item" />
    </div>
  );
};

export default WatchlistItemHeader;
