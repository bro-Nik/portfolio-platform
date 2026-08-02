import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { Modal, Input, Spin, Empty, Tooltip } from 'antd';
import { Search } from 'lucide-react';
import TickerAvatar from 'src/components/TickerAvatar';
import { useModalStore } from '@portfolio/shared';
import { usePortfolioOperations } from '../../hooks/usePortfolioOperations';
import { useTickersQuery } from 'src/modules/assets/hooks/useTickersQuery';
import { useNotifications } from '@portfolio/shared';

const AssetAddModal = () => {
  const { success, error } = useNotifications();
  const { modalProps, closeModal } = useModalStore();
  const { portfolio } = modalProps;
  const { addAsset } = usePortfolioOperations();

  const existingTickerIds = useMemo(
    () => new Set(portfolio.assets?.map(a => a.tickerId) || []),
    [portfolio.assets]
  );

  const [searchValue, setSearchValue] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const listRef = useRef();

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchValue), 300);
    return () => clearTimeout(timer);
  }, [searchValue]);

  const {
    data,
    isFetching,
    isFetchingNextPage,
    fetchNextPage,
    hasNextPage,
  } = useTickersQuery(portfolio.market, debouncedSearch);

  const tickers = useMemo(
    () => data?.pages.flatMap(p => p.data) ?? [],
    [data]
  );

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [debouncedSearch]);

  const handleScroll = useCallback((e) => {
    const { scrollTop, clientHeight, scrollHeight } = e.currentTarget;
    if (scrollHeight - scrollTop <= clientHeight * 1.5 && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  const getAssetImage = (ticker) => {
    return import.meta.env.VITE_IMAGE_BASE_URL + ticker.market + '/24/' + ticker.image;
  };

  const handleSelect = async (ticker) => {
    if (existingTickerIds.has(ticker.id)) return;
    const result = await addAsset(portfolio, ticker);

    if (result.success) {
      success('Актив успешно добавлен в портфель');
      closeModal();
    } else {
      error(result.error || 'Произошла ошибка при добавлении актива');
    }
  };

  const handleCancel = () => {
    closeModal();
  };

  const renderTickerItem = (ticker) => {
    const isDisabled = existingTickerIds.has(ticker.id);

    return (
    <div
      key={ticker.id}
      style={{ 
        padding: 0,
        marginBottom: 12,
        border: 'none',
      }}
    >
      <Tooltip title={isDisabled ? 'Актив уже добавлен в портфель' : ''}>
      <div
        className="ticker-item"
        onClick={() => !isDisabled && handleSelect(ticker)}
        style={isDisabled ? { opacity: 0.5, cursor: 'not-allowed' } : undefined}
      >
        <div style={{ flexShrink: 0 }}>
          <TickerAvatar
            src={ticker.image ? getAssetImage(ticker) : null}
            symbol={ticker.symbol}
            size={24}
          />
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 8,
            marginBottom: 4,
          }}>
            <span style={{ 
              fontSize: '14px', 
              fontWeight: 500,
              color: 'var(--text-primary)',
              lineHeight: 1.4,
            }}>
              {ticker.name}
            </span>
            
            {ticker.marketCapRank && (
              <span style={{ 
                fontSize: '11px',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                backgroundColor: 'rgba(111, 118, 126, 0.1)',
                padding: '2px 6px',
                borderRadius: 4,
                lineHeight: 1,
                whiteSpace: 'nowrap',
              }}>
                #{ticker.marketCapRank}
              </span>
            )}
          </div>

          <div style={{ 
            fontSize: '13px',
            color: 'var(--text-secondary)',
            lineHeight: 1.3,
            textTransform: 'uppercase',
          }}>
            {ticker.symbol}
          </div>
        </div>

        <div style={{ 
          flexShrink: 0,
          textAlign: 'right',
        }}>
          <div style={{ 
            fontSize: '14px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            lineHeight: 1.4,
          }}>
            ${ticker.price.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </div>
          <div style={{ 
            fontSize: '12px',
            color: 'var(--text-secondary)',
            lineHeight: 1.3,
          }}>
            {ticker.market}
          </div>
        </div>
      </div>
      </Tooltip>
    </div>
    );
  };

  return (
    <Modal
      title="Добавить актив в портфель"
      open={true}
      onCancel={handleCancel}
      footer={null}
      width={600}
      style={{ top: 20 }}
      destroyOnHidden
    >
      <div style={{ marginBottom: 16, position: 'relative' }}>
        <Input
          style={{ border: 'none' }}
          placeholder="Введите тикер или название актива..."
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          prefix={<Search size={16} style={{ color: 'var(--text-muted-icon)' }} />}
          size="large"
          allowClear
        />
      </div>

      <div
        ref={listRef}
        onScroll={handleScroll}
        style={{ height: 400, overflow: 'auto' }}
      >
        {tickers.length > 0
          ? tickers.map(renderTickerItem)
          : (isFetching ? <Spin size="large" /> : <Empty description="Активы не найдены" />)
        }
        
        {isFetchingNextPage && tickers.length > 0 && (
          <div style={{ textAlign: 'center', padding: '12px' }}>
            <Spin size="small" />
          </div>
        )}
      </div>
    </Modal>
  );
};

export default AssetAddModal;
