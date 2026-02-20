import React from 'react';
import { formatCurrency, formatPercentage, formatProfit, getColorClass } from '/app/src/utils/format';
import StatisticCards from '/app/src/features/statistics/StatisticCards';

const AssetStatistic = ({ portfolio, asset }) => {

  const statCards = [
    {
      title: 'Количество',
      value: `${asset.quantity || 0} ${asset.symbol}`,
      description: ''
    },
    {
      title: 'Средняя цена',
      value: formatCurrency(asset.averagePrice || 0),
      description: ''
    },
    {
      title: 'Стоимость',
      value: formatCurrency(asset.costNow || 0),
      description: 'Общая стоимость активов по текущим ценам'
    },
    {
      title: 'Вложено',
      value: formatCurrency(asset.invested || 0),
      description: 'Общая сумма инвестиций'
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
      title: 'Прибыль',
      value: formatProfit(asset.profit || 0, asset.invested || 0),
      class: getColorClass(asset.profit),
      description: 'Прибыль/убыток за все время'
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default AssetStatistic;
