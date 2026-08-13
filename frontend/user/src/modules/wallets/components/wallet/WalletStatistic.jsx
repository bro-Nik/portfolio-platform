import React from 'react';
import { formatCurrencyFromUsd, formatPercentage } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';
import { useDisplayCurrency } from 'src/utils/currency';

const WalletStatistic = ({ wallet }) => {
  useDisplayCurrency();
  const statCards = [
    {
      title: 'Стоимость',
      value: formatCurrencyFromUsd(wallet.costNow),
    },
    {
      title: 'Доля',
      value: formatPercentage(wallet.share),
    },
    {
      title: 'Ордера на покупку',
      value: formatCurrencyFromUsd(wallet.buyOrders),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default WalletStatistic;
