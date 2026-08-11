import { formatCurrencyFromUsd, formatProfit, formatQuantity, getColorClass } from 'src/utils/format';
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
      title: 'Средняя цена',
      value: formatCurrencyFromUsd(asset.averagePrice || 0, true),
    },
    {
      title: 'Стоимость',
      value: formatCurrencyFromUsd(asset.costNow || 0),
    },
    {
      title: 'Вложено',
      value: formatCurrencyFromUsd(asset.invested || 0),
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
      title: 'Прибыль',
      value: formatProfit(asset.profit || 0, asset.invested || 0, asset.totalInvested),
      class: getColorClass(asset.profit),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default AssetStatistic;
