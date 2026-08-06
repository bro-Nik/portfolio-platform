import React, { useMemo } from 'react';
import { Card, Row, Col, Typography, Space } from 'antd';
import { PieChart, Wallet } from 'lucide-react';
import RichTooltip from 'src/components/RichTooltip';
import { formatCurrency, formatQuantity, formatPercentage } from 'src/utils/format';
import { useWalletsData } from 'src/modules/wallets/hooks/useWalletsData';
import { usePortfoliosData } from 'src/modules/portfolios/hooks/usePortfoliosData';

const { Text } = Typography;

const SegmentedProgress = ({ segments, totalAmount, symbol }) => {
  if (!segments.length) {
    return (
      <RichTooltip
        title={
          <div style={{ maxWidth: 300 }}>
            <Text strong style={{ display: 'block', marginBottom: 8 }}>
              Всего: {formatCurrency(0)}
            </Text>
            <Text type="secondary" style={{ fontSize: 13 }}>
              Актива нигде нет
            </Text>
          </div>
        }
      >
        <div style={{ position: 'relative', cursor: 'pointer' }}>
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
      </RichTooltip>
    );
  }

  // Вычисляем позиции для сегментов
  const positionedSegments = segments.reduce((acc, segment) => {
    const start = acc.length ? acc[acc.length - 1].end : 0;
    acc.push({
      ...segment,
      start,
      end: start + segment.percent,
    });
    return acc;
  }, []);

  return (
    <RichTooltip
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
              <Space orientation="vertical" size={0} style={{ marginLeft: 16 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {formatCurrency(segment.costNow)} ({formatPercentage(segment.percent)})
                </Text>
                <Text type="secondary" style={{ fontSize: 11 }}>
                  {formatQuantity(segment.quantity)} {symbol?.toUpperCase()}
                </Text>
              </Space>
            </div>
          ))}
        </div>
      }
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
    </RichTooltip>
  );
};

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
  return (
    <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
      <Col xs={24} md={12}>
        <Card 
          variant="borderless"
          styles={{ body: { padding: 24 } }}
          style={{ borderRadius: 12 }}
        >
          <Space orientation="vertical" size={16} style={{ width: '100%' }}>
            <Space align="center">
              <PieChart size={16} />
              <Text>Распределение по портфелям</Text>
            </Space>

            <SegmentedProgress segments={portfolioSegments} totalAmount={totalPortfolioCost} symbol={data.symbol} />
          </Space>
        </Card>
      </Col>

      <Col xs={24} md={12}>
        <Card 
          variant="borderless"
          styles={{ body: { padding: 24 } }}
          style={{ borderRadius: 12 }}
        >
          <Space orientation="vertical" size={16} style={{ width: '100%' }}>
            <Space align="center">
              <Wallet size={16} />
              <Text>Распределение по кошелькам</Text>
            </Space>

            <SegmentedProgress segments={walletSegments} totalAmount={totalWalletCost} symbol={data.symbol} />
          </Space>
        </Card>
      </Col>
    </Row>
  );
};

export default AssetDetail;
