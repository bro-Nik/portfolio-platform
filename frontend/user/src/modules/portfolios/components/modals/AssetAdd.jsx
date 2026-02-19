import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Modal, Input, List, Avatar, Spin, Empty, Button, message } from 'antd';
import { SearchOutlined, CloseOutlined } from '@ant-design/icons';
import { useModalStore } from '/app/src/stores/modalStore';
import { assetApi } from '/app/src/modules/assets/api/assetApi';
import { usePortfolioOperations } from '../../hooks/usePortfolioOperations';

const AssetAddModal = () => {
  const { modalProps, closeModal } = useModalStore();
  const { portfolio } = modalProps;
  const { addAsset, loading: addLoading } = usePortfolioOperations();

  const [loading, setLoading] = useState(false);
  const [tickers, setTickers] = useState([]);
  const [searchValue, setSearchValue] = useState('');
  const [hasMore, setHasMore] = useState(true);
  const [initialLoad, setInitialLoad] = useState(false);
  
  const pageRef = useRef(1);
  const searchRef = useRef('');
  const listRef = useRef();

  const getAssetImage = (ticker) => {
    const imagePath = process.env.REACT_APP_IMAGE_BASE_URL + ticker.market + '/24/' + ticker.image;
    return imagePath
  };

  // Загрузка данных
  const loadTickers = useCallback(
    async (search, page, append = false) => {
      setLoading(true);

      const result = await assetApi.getTickersByMarket(portfolio.market, search, page);
      if (result.success) {
        const { data, has_more } = result.data;
        if (append) {
          setTickers(prev => [...prev, ...data]);
        } else {
          setTickers(data);
          // Скроллим к верху при новом поиске
          if (listRef.current) {
            // listRef.current.scrollTo(0);
            listRef.current.scrollTo({ top: 0, behavior: 'smooth' });
          }
        }
        setHasMore(has_more);
      }
        
      setLoading(false);
    },
    [portfolio.market]
  );

  // Обработчик поиска с дебаунсом
  const handleSearch = useCallback(
    debounce((value: string) => {
      searchRef.current = value;
      pageRef.current = 1;
      loadTickers(value, 1, false);
    }, 300),
    [loadTickers]
  );

  // Обработчик изменения поискового запроса
  const handleSearchChange = (value: string) => {
    setSearchValue(value);
    handleSearch(value);
  };

  // Очистка поиска
  const handleClearSearch = () => {
    setSearchValue('');
    searchRef.current = '';
    pageRef.current = 1;
    loadTickers('', 1, false);
  };

  // Загрузка при открытии модального окна
  useEffect(() => {
    if (!initialLoad) {
      loadTickers('', 1, false);
      setInitialLoad(true);
    }
  }, [initialLoad, loadTickers]);

  // Обработчик скролла для ленивой загрузки
  const handleScroll = (e) => {
    const { scrollTop, clientHeight, scrollHeight } = e.currentTarget;
    
    // Загружаем следующую страницу
    if (scrollHeight - scrollTop <= clientHeight * 1.5 && hasMore && !loading) {
      pageRef.current += 1;
      loadTickers(searchRef.current, pageRef.current, true);
    }
  };

  // Обработчик выбора актива
  const handleSelect = async (ticker: Ticker) => {
    const result = await addAsset(portfolio, ticker);

    if (result.success) {
      message.success('Актив успешно добавлен в портфель');
      closeModal();
    } else {
      message.error(result.error || 'Произошла ошибка при добавлении актива');
    }
  };

  // Сброс состояния при закрытии
  const handleCancel = () => {
    // setSearchValue('');
    // setTickers([]);
    // setHasMore(true);
    // pageRef.current = 1;
    // searchRef.current = '';
    closeModal();
  };

  const renderTickerItem = (ticker: Ticker) => (
    <List.Item
      key={ticker.id}
      style={{ 
        padding: 0,
        marginBottom: 12,
        border: 'none',
      }}
    >
      <div
        className="ticker-item"
        style={{
          display: 'flex',
          alignItems: 'center',
          background: '#F8FAFD',
          borderRadius: 8,
          padding: '8px',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          gap: '12px',
          width: '100%',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = '#EDF2FF';
          e.currentTarget.style.transform = 'translateY(-1px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = '#F8FAFD';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
        onClick={() => handleSelect(ticker)}
      >
        {/* Иконка */}
        <div style={{ flexShrink: 0 }}>
          {ticker.image ? (
            <Avatar 
              src={getAssetImage(ticker)} 
              size={24}
              style={{ minWidth: 24 }}
            />
          ) : (
            <Avatar 
              size={24}
              style={{ 
                backgroundColor: '#1890ff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '10px',
                minWidth: 24,
              }}
            >
              {ticker.symbol.slice(0, 2).toUpperCase()}
            </Avatar>
          )}
        </div>

        {/* Основная информация */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Верхняя строка: название и бейдж */}
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 8,
            marginBottom: 4,
          }}>
            <span style={{ 
              fontSize: '14px', 
              fontWeight: 500,
              color: '#1A1D1F',
              lineHeight: 1.4,
            }}>
              {ticker.name}
            </span>
            
            {ticker.market_cap_rank && (
              <span style={{ 
                fontSize: '11px',
                fontWeight: 600,
                color: '#6F767E',
                backgroundColor: 'rgba(111, 118, 126, 0.1)',
                padding: '2px 6px',
                borderRadius: 4,
                lineHeight: 1,
                whiteSpace: 'nowrap',
              }}>
                #{ticker.market_cap_rank}
              </span>
            )}
          </div>

          {/* Нижняя строка: символ */}
          <div style={{ 
            fontSize: '13px',
            color: '#6F767E',
            lineHeight: 1.3,
            textTransform: 'uppercase',
          }}>
            {ticker.symbol}
          </div>
        </div>

        {/* Цена */}
        <div style={{ 
          flexShrink: 0,
          textAlign: 'right',
        }}>
          <div style={{ 
            fontSize: '14px',
            fontWeight: 600,
            color: '#1A1D1F',
            lineHeight: 1.4,
          }}>
            ${ticker.price.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </div>
          <div style={{ 
            fontSize: '12px',
            color: '#6F767E',
            lineHeight: 1.3,
          }}>
            {ticker.market}
          </div>
        </div>
      </div>
    </List.Item>
  );

  return (
    <Modal
      title="Добавить актив в портфель"
      open={true}
      onCancel={handleCancel}
      footer={null}
      width={600}
      style={{ top: 20 }}
      destroyOnClose
      centered
    >
      {/* Строка поиска */}
      <div style={{ marginBottom: 16, position: 'relative' }}>
        <Input
          style={{ border: 'none' }}
          placeholder="Введите тикер или название актива..."
          value={searchValue}
          onChange={(e) => handleSearchChange(e.target.value)}
          prefix={<SearchOutlined style={{ color: '#ccc' }} />}
          size="large"
          allowClear
        />
      </div>

      {/* Список активов */}
      <div
        ref={listRef}
        onScroll={handleScroll}
        style={{ height: 400, overflow: 'auto' }}
      >
        <List
          dataSource={tickers}
          renderItem={renderTickerItem}
          locale={{
            emptyText: loading ? <Spin size="large" /> : <Empty description="Активы не найдены" />
          }}
        />
        
        {/* Индикатор загрузки при подгрузке */}
        {loading && tickers.length > 0 && (
          <div style={{ textAlign: 'center', padding: '12px' }}>
            <Spin size="small" />
          </div>
        )}
      </div>
    </Modal>
  );
};

// Хук для дебаунса
function debounce(func, wait) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export default AssetAddModal;
