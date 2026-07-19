import { useQuery } from '@tanstack/react-query';
import { fetchOverview } from '../api/overviewApi';

export const useOverviewQuery = () => useQuery({
  queryKey: ['overview'],
  queryFn: fetchOverview,
});
