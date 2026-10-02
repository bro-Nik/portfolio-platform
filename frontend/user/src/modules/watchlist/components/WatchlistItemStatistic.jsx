import React, { useMemo } from 'react';
import StatisticCards from 'src/features/statistics/StatisticCards';
import { isTriggered } from '../utils/alerts';

export const WatchlistItemStatistic = ({ item }) => {
  const stats = useMemo(() => {
    const alerts = item.alerts || [];
    return {
      active: alerts.filter(a => a.isActive && !a.isArchived).length,
      triggered: alerts.filter(isTriggered).length,
    };
  }, [item.alerts]);

  const statCards = [
    {
      title: 'Активных уведомлений',
      value: String(stats.active),
    },
    {
      title: 'Сработавших',
      value: String(stats.triggered),
    },
  ];

  return <StatisticCards cards={statCards} />;
};

export default WatchlistItemStatistic;
