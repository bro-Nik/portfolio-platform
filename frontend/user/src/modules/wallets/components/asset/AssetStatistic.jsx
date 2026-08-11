import React from 'react';
import { formatCurrency, formatCurrencyFromUsd, formatQuantity } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';
import { useDisplayCurrency } from 'src/utils/currency';

const AssetStatistic = ({ asset }) => {
  useDisplayCurrency();

  const statCards = [
    {
      title: 'Количество',
      value: `${formatQuantity(asset.quantity)} ${asset.symbol?.toUpperCase()}`,
    },
    {
      title: 'Стоимость',
      value: formatCurrencyFromUsd(asset.costNow || 0),
    },
    {
      title: 'В ордерах на покупку',
      value: formatCurrencyFromUsd(asset.buyOrders || 0),
    },
    {
      title: 'В ордерах на продажу',
      value: formatCurrencyFromUsd(asset.sellOrders || 0),
    },
    {
      title: 'Свободно',
      value: formatCurrency(asset.free || 0, asset.symbol),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default AssetStatistic;
