import React from 'react';
import { formatCurrency } from '/app/src/utils/format';
import StatisticCards from '/app/src/features/statistics/StatisticCards';

const AssetStatistic = ({ portfolio, asset }) => {

  const statCards = [
    {
      title: 'Количество',
      value: `${asset.quantity || 0} ${asset.symbol}`,
      description: ''
    },
    {
      title: 'Стоимость',
      value: formatCurrency(asset.costNow || 0),
      description: 'Общая стоимость активов по текущим ценам'
    },
    {
      title: 'В ордерах на покупку',
      value: formatCurrency(asset.buyOrders || 0),
      description: ''
    },
    {
      title: 'В ордерах на продажу',
      value: formatCurrency(asset.sellOrders || 0),
      description: ''
    },
    {
      title: 'Свободно',
      value: formatCurrency(asset.free || 0, asset.symbol),
      description: 'Прибыль/убыток за все время'
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default AssetStatistic;
