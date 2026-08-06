import { formatCurrency, formatProfit, formatQuantity, getColorClass } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';

const AssetStatistic = ({ asset }) => {

  const statCards = [
    {
      title: 'Количество',
      value: `${formatQuantity(asset.quantity)} ${asset.symbol?.toUpperCase()}`,
    },
    {
      title: 'Средняя цена',
      value: formatCurrency(asset.averagePrice || 0),
    },
    {
      title: 'Стоимость',
      value: formatCurrency(asset.costNow || 0),
    },
    {
      title: 'Вложено',
      value: formatCurrency(asset.invested || 0),
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
      value: formatProfit(asset.profit || 0, asset.invested || 0, asset.totalInvested),
      class: getColorClass(asset.profit),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default AssetStatistic;
