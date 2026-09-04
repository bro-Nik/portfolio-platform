import { getPortfolios } from 'src/api';

const portfolios = getPortfolios();

export const fetchOverview = () => portfolios.getUserOverviewApiOverviewGet();
