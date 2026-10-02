import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { Modal, Input, Spin, Empty, Tooltip, Segmented } from 'antd';
import { Search } from 'lucide-react';
import TickerAvatar from 'src/components/TickerAvatar';
import { useModalStore, useNotifications, useDebounce } from '@portfolio/shared';
import { useTickersQuery } from 'src/modules/assets/hooks/useTickersQuery';
import { getTickerImage } from 'src/modules/assets/utils/assetUtils';
import { getMarketLabel } from 'src/constants/markets';
import { formatCurrencyFromUsd } from 'src/utils/format';
import { useDisplayCurrency } from 'src/utils/currency';
import { useWatchlistOperations } from '../../hooks/useWatchlistOperations';
import { useWatchlistQuery } from '../../hooks/useWatchlistQuery';

const MARKETS = ['crypto', 'stocks', 'currency'];

const WatchlistAssetAddModal = () => {
  useDisplayCurrency();
  const { success, error } = useNotifications();
  const { closeModal } = useModalStore();
  const { addItem, loading } = useWatchlistOperations();
  const { data: items = [] } = useWatchlistQuery();

  const existingTickerIds = useMemo(() => new Set(items.map(i => i.tickerId)), [items]);

  const [selectedMarket, setSelectedMarket] = useState('crypto');
  const [searchValue, setSearchValue] = useState('');
  const debouncedSearch = useDebounce(searchValue, 300);
  const listRef = useRef();

  const {
    data,
    isFetching,
    isFetchingNextPage,
    fetchNextPage,
    hasNextPage,
  } = useTickersQuery([selectedMarket], debouncedSearch);

  const tickers = useMemo(() => data?.pages.flatMap(p => p.data) ?? [], [data]);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [debouncedSearch, selectedMarket]);

  const handleScroll = useCallback((e) => {
    const { scrollTop, clientHeight, scrollHeight } = e.currentTarget;
    if (scrollHeight - scrollTop <= clientHeight * 1.5 && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  const handleSelect = async (ticker) => {
    if (existingTickerIds.has(ticker.id) || loading) return;
    const result = await addItem(ticker, null);
    if (result.success) {
      success('Актив добавлен в избранное');
      closeModal();
    } else {
      error(result.error || 'Произошла ошибка при добавлении актива');
    }
  };

  const renderTickerItem = (ticker) => {
    const isDisabled = existingTickerIds.has(ticker.id);

    return (
      <div key={ticker.id} style={{ padding: 0, marginBottom: 12, border: 'none' }}>
        <Tooltip title={isDisabled ? 'Актив уже в избранном' : ''}>
          <div
            className="ticker-item"
            onClick={() => !isDisabled && handleSelect(ticker)}
            style={isDisabled ? { opacity: 0.5, cursor: 'not-allowed' } : undefined}
          >
            <div style={{ flexShrink: 0 }}>
              <TickerAvatar
                src={ticker.image ? getTickerImage(ticker) : null}
                symbol={ticker.symbol}
                size={24}
              />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)', lineHeight: 1.4 }}>
                  {ticker.name}
                </span>
                {ticker.marketCapRank && (
                  <span style={{
                    fontSize: '11px', fontWeight: 600, color: 'var(--text-secondary)',
                    backgroundColor: 'rgba(111, 118, 126, 0.1)', padding: '2px 6px',
                    borderRadius: 4, lineHeight: 1, whiteSpace: 'nowrap',
                  }}>
                    #{ticker.marketCapRank}
                  </span>
                )}
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.3, textTransform: 'uppercase' }}>
                {ticker.symbol}
              </div>
            </div>
            <div style={{ flexShrink: 0, textAlign: 'right' }}>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.4 }}>
                {formatCurrencyFromUsd(ticker.price, true)}
              </div>
            </div>
          </div>
        </Tooltip>
      </div>
    );
  };

  return (
    <Modal
      title="Добавить в избранное"
      open={true}
      onCancel={closeModal}
      footer={null}
      width={600}
      style={{ top: 20 }}
      destroyOnHidden
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <Segmented
          options={MARKETS.map(m => ({ value: m, label: getMarketLabel(m) }))}
          value={selectedMarket}
          onChange={(value) => { setSelectedMarket(value); setSearchValue(''); }}
          style={{ flexShrink: 0 }}
        />
        <div style={{ position: 'relative', flex: 1 }}>
          <Input
            prefix={<Search size={16} style={{ color: 'var(--text-muted-icon)' }} />}
            placeholder="Введите тикер или название актива..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            allowClear
            variant="filled"
          />
        </div>
      </div>
      <div ref={listRef} onScroll={handleScroll} style={{ height: 400, overflow: 'auto' }}>
        {tickers.length > 0
          ? tickers.map(renderTickerItem)
          : (isFetching ? <div style={{ textAlign: 'center', padding: 24 }}><Spin size="large" /></div> : <Empty description="Активы не найдены" />)
        }
        {isFetchingNextPage && <div style={{ textAlign: 'center', padding: 12 }}><Spin size="small" /></div>}
      </div>
    </Modal>
  );
};

export default WatchlistAssetAddModal;
