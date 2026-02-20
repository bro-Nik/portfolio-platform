import React, { useMemo } from 'react';
import { Card, Row, Col, Progress, Tooltip, Typography, Space } from 'antd';
import { PieChartOutlined, WalletOutlined } from '@ant-design/icons';
import { formatCurrency, formatPercentage } from '/app/src/utils/format';
import { useWalletsData } from '/app/src/modules/wallets/hooks/useWalletsData';
import { usePortfoliosData } from '/app/src/modules/portfolios/hooks/usePortfoliosData';

const { Text } = Typography;

const AssetDetail = ({ data }) => {
  const { portfolios } = usePortfoliosData();
  const { wallets } = useWalletsData();

  const itemHoldings = (items, tickerId) => {
    if (!items || !tickerId) return [];
    
    return items
      .flatMap(item => 
        item.assets
          ?.filter(a => a.tickerId === data.tickerId && a.quantity > 0 && a.costNow > 0.01)  // Отсекаем мелкий баланс
          .map(a => ({
            name: item.name,
            quantity: a.quantity,
            costNow: a.costNow || 0,
          })) || []
      )
      .filter(Boolean);
  };

  const portfolioHoldings = useMemo(() => {
    return itemHoldings(portfolios, data?.tickerId)
  }, [portfolios, data?.tickerId]);

  const { portfolioHoldingsWithPercentage, totalPortfolioCost } = useMemo(() => {
    const total = portfolioHoldings.reduce((sum, item) => sum + item.costNow, 0);
    
    const holdingsWithPercentage = portfolioHoldings.map(item => ({
      ...item,
      percentageOfTotal: total > 0 ? (item.costNow / total) * 100 : 0
    }));

    return {
      portfolioHoldingsWithPercentage: holdingsWithPercentage,
      totalPortfolioCost: total
    };
  }, [portfolioHoldings]);

  const walletHoldings = useMemo(() => {
    return itemHoldings(wallets, data?.tickerId)
  }, [wallets, data?.tickerId]);

  const { walletHoldingsWithPercentage, totalWalletCost } = useMemo(() => {
    const total = walletHoldings.reduce((sum, item) => sum + item.costNow, 0);
    
    const holdingsWithPercentage = walletHoldings.map(item => ({
      ...item,
      percentageOfTotal: total > 0 ? (item.costNow / total) * 100 : 0
    }));

    return {
      walletHoldingsWithPercentage: holdingsWithPercentage,
      totalWalletCost: total
    };
  }, [walletHoldings]);

  // Подготавливаем сегменты для прогресс-баров
  const portfolioSegments = useMemo(() => 
    portfolioHoldingsWithPercentage.map((p, i) => ({
      percent: +p.percentageOfTotal,
      color: ['#1890ff', '#52c41a', '#fa8c16', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96'][i % 7],
      name: p.name,
      costNow: p.costNow,
      quantity: p.quantity
    })).sort((a, b) => b.percent - a.percent),
    [portfolioHoldingsWithPercentage]
  );

  const walletSegments = useMemo(() => 
    walletHoldingsWithPercentage.map((w, i) => ({
      percent: +w.percentageOfTotal,
      color: ['#1890ff', '#52c41a', '#fa8c16', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96'][i % 7],
      name: w.name,
      costNow: w.costNow,
      quantity: w.quantity
    })).sort((a, b) => b.percent - a.percent),
    [walletHoldingsWithPercentage]
  );

  // Функция для создания прогресс-бара с сегментами
  const SegmentedProgress = ({ segments, totalAmount }) => {
    if (!segments.length) {
      return (
        <div style={{ position: 'relative', cursor: 'pointer' }}>
          
          {/* Отображаем сегменты */}
          <div style={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            right: 0, 
            height: 12,
            borderRadius: 8,
            overflow: 'hidden',
            display: 'flex'
          }}>
            <div
              style={{
                width: '100%',
                backgroundColor: '#ababab',
                opacity: '0.5'
              }}
            />
          </div>
        </div>
      );
    }

    // Вычисляем позиции для сегментов
    let currentPosition = 0;
    const positionedSegments = segments.map(segment => {
      const segmentData = {
        ...segment,
        start: currentPosition,
        end: currentPosition + segment.percent
      };
      currentPosition += segment.percent;
      return segmentData;
    });

    return (
      <Tooltip
        title={
          <div style={{ maxWidth: 300 }} >
            <Text strong style={{ display: 'block', marginBottom: 8 }}>
              Всего: {formatCurrency(totalAmount)}
            </Text>
            {positionedSegments.map((segment, index) => (
              <div key={index} style={{ marginBottom: 6 }}>
                <Space align="center" style={{ marginBottom: 4 }}>
                  <div 
                    style={{
                      width: 10,
                      height: 10,
                      backgroundColor: segment.color,
                      borderRadius: 2
                    }}
                  />
                  <Text strong style={{ fontSize: 13 }}>{segment.name}</Text>
                </Space>
                <Space direction="vertical" size={0} style={{ marginLeft: 16 }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {formatCurrency(segment.costNow)} ({formatPercentage(segment.percent)})
                  </Text>
                  <Text type="secondary" style={{ fontSize: 11 }}>
                    {segment.quantity} {data.symbol}
                  </Text>
                </Space>
              </div>
            ))}
          </div>
        }
        color="white"
        overlayStyle={{ 
          maxWidth: 350,
          boxShadow: '0 3px 6px -4px rgba(0,0,0,0.12), 0 6px 16px 0 rgba(0,0,0,0.08), 0 9px 28px 8px rgba(0,0,0,0.05)'
        }}
        placement="top"
      >
        <div style={{ position: 'relative', cursor: 'pointer' }}>
          
          {/* Отображаем сегменты */}
          <div style={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            right: 0, 
            height: 12,
            borderRadius: 8,
            overflow: 'hidden',
            display: 'flex'
          }}>
            {positionedSegments.map((segment, index) => (
              <div
                key={index}
                style={{
                  width: `${segment.percent}%`,
                  backgroundColor: segment.color,
                  transition: 'opacity 0.2s',
                  opacity: '0.5'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '0.9';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '0.5';
                }}
              />
            ))}
          </div>
        </div>
      </Tooltip>
    );
  };

  return (
    <Row gutter={[24, 24]} className='mb-4'>
      <Col xs={24} md={12}>
        <Card 
          bordered={false}
          bodyStyle={{ padding: 24 }}
          style={{ 
            backgroundColor: '#fafafa',
            borderRadius: 12 
          }}
        >
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Space align="center">
              <PieChartOutlined />
              <Text>Распределение по портфелям</Text>
            </Space>

            <SegmentedProgress segments={portfolioSegments} totalAmount={totalPortfolioCost} />
          </Space>
        </Card>
      </Col>

      <Col xs={24} md={12}>
        <Card 
          bordered={false}
          bodyStyle={{ padding: 24 }}
          style={{ 
            backgroundColor: '#fafafa',
            borderRadius: 12 
          }}
        >
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Space align="center">
              <WalletOutlined />
              <Text>Распределение по кошелькам</Text>
            </Space>

            <SegmentedProgress segments={walletSegments} totalAmount={totalWalletCost} />
          </Space>
        </Card>
      </Col>
    </Row>
  );
};

export default AssetDetail;
