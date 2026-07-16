import { useQuery } from '@tanstack/react-query';
import { portfolioApi } from '../../modules/portfolios/api/portfolioApi';

export const usePortfoliosQuery = () => {
  return useQuery({
    queryKey: ['portfolios'],
    queryFn: () => portfolioApi.getPortfolios(),
    refetchOnWindowFocus: false,
  });
};
