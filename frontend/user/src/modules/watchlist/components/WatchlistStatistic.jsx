import React from 'react';
import StatisticCards from 'src/features/statistics/StatisticCards';

export const WatchlistStatistic = ({ stats }) => {
  const statCards = [
    {
      title: 'Активов',
      value: String(stats.totalItems || 0),
    },
    {
      title: 'Активных уведомлений',
      value: String(stats.activeAlerts || 0),
    },
    {
      title: 'Сработавших',
      value: String(stats.triggeredAlerts || 0),
    },
  ];

  return <StatisticCards cards={statCards} />;
};

export default WatchlistStatistic;
