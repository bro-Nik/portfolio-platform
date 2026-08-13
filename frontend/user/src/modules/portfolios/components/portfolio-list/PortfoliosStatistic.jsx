import React from 'react';
import { formatCurrencyFromUsd, formatProfit, getColorClass } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';
import { useDisplayCurrency } from 'src/utils/currency';

const PortfoliosStatistic = ({ stats }) => {
  useDisplayCurrency();
  const statCards = [
    {
      title: 'Стоимость',
      value: formatCurrencyFromUsd(stats.totalCostNow || 0),
    },
    {
      title: 'Вложено',
      value: formatCurrencyFromUsd(stats.totalInvested || 0),
    },
    {
      title: 'Прибыль',
      value: formatProfit(stats.totalProfit || 0, stats.totalInvested || 0, stats.totalCapitalDeployed),
      class: getColorClass(stats.totalProfit),
    },
    {
      title: 'Ордера на покупку',
      value: formatCurrencyFromUsd(stats.totalBuyOrders || 0),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default PortfoliosStatistic;
