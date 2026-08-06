import React from 'react';
import { formatCurrency, formatQuantity } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';

const AssetStatistic = ({ asset }) => {

  const statCards = [
    {
      title: 'Количество',
      value: `${formatQuantity(asset.quantity)} ${asset.symbol?.toUpperCase()}`,
    },
    {
      title: 'Стоимость',
      value: formatCurrency(asset.costNow || 0),
    },
    {
      title: 'В ордерах на покупку',
      value: formatCurrency(asset.buyOrders || 0),
    },
    {
      title: 'В ордерах на продажу',
      value: formatCurrency(asset.sellOrders || 0),
    },
    {
      title: 'Свободно',
      value: formatCurrency(asset.free || 0, asset.symbol),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default AssetStatistic;
