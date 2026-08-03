import React, { useEffect, useMemo, useState } from 'react';
import { Spin, Empty } from 'antd';
import FormSelect from './FormSelect';
import TickerAvatar from 'src/components/TickerAvatar';
import { useTickersQuery } from 'src/modules/assets/hooks/useTickersQuery';
import { getTickerImage } from 'src/modules/assets/utils/assetUtils';

const AssetSelect = ({ markets, label = 'Актив', placeholder = 'Введите название или тикер...', onTickerChange, ...props }) => {
  const [searchValue, setSearchValue] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchValue), 300);
    return () => clearTimeout(timer);
  }, [searchValue]);

  const {
    data,
    isFetching,
    fetchNextPage,
    hasNextPage,
  } = useTickersQuery(markets, debouncedSearch);

  const tickers = useMemo(() => data?.pages.flatMap(p => p.data) ?? [], [data]);

  const handleChange = (value) => {
    const ticker = tickers.find(t => t.id === value);
    onTickerChange?.(ticker);
  };

  const handlePopupScroll = (e) => {
    const { scrollTop, clientHeight, scrollHeight } = e.currentTarget;
    if (scrollHeight - scrollTop <= clientHeight * 1.5 && hasNextPage) {
      fetchNextPage();
    }
  };

  return (
    <FormSelect
      {...props}
      label={label}
      placeholder={placeholder}
      showSearch
      filterOption={false}
      onChange={handleChange}
      onSearch={setSearchValue}
      onPopupScroll={handlePopupScroll}
      notFoundContent={isFetching ? <Spin size="small" style={{ padding: 8 }} /> : <Empty description="Активы не найдены" style={{ padding: 8 }} />}
      fieldNames={{ label: 'symbol', value: 'id' }}
      options={tickers}
      optionRender={(o) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <TickerAvatar src={getTickerImage(o.data)} symbol={o.data.symbol} size={20} />
          <span>{o.data.name}</span>
          <span style={{ color: 'var(--text-muted)', textTransform: 'uppercase', marginLeft: 'auto' }}>{o.data.symbol}</span>
        </div>
      )}
    />
  );
};

export default AssetSelect;
