import React from 'react';
import { formatCurrency, formatProfit, getColorClass } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';

const PortfoliosStatistic = ({ stats }) => {
  const statCards = [
    {
      title: 'Стоимость',
      value: formatCurrency(stats.totalCostNow || 0),
    },
    {
      title: 'Вложено',
      value: formatCurrency(stats.totalInvested || 0),
    },
    {
      title: 'Прибыль',
      value: formatProfit(stats.totalProfit || 0, stats.totalInvested || 0, stats.totalCapitalDeployed),
      class: getColorClass(stats.totalProfit),
    },
    {
      title: 'В ордерах',
      value: formatCurrency(stats.totalBuyOrders || 0),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default PortfoliosStatistic;
