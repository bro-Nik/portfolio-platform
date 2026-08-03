import React from 'react';
import { formatCurrency, formatProfit, getColorClass } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';

const AssetStatistic = ({ asset }) => {

  const statCards = [
    {
      title: 'Количество',
      value: `${asset.quantity || 0} ${asset.symbol?.toUpperCase()}`,
    },
    {
      title: 'Средняя цена',
      value: asset.averagePrice == null ? '-' : formatCurrency(asset.averagePrice || 0),
    },
    {
      title: 'Стоимость',
      value: formatCurrency(asset.costNow || 0),
    },
    {
      title: 'Вложено',
      value: asset.invested ? formatCurrency(asset.invested || 0) : '-',
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
      title: 'Прибыль',
      value: asset.profit == null ? '-' : formatProfit(asset.profit || 0, asset.invested || 0, asset.totalInvested),
      class: getColorClass(asset.profit),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default AssetStatistic;
