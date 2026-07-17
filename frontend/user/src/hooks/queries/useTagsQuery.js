import { useQuery } from '@tanstack/react-query';
import { tagApi } from '../../modules/portfolios/api/tagApi';

export const useTagsQuery = () => {
  return useQuery({
    queryKey: ['tags'],
    queryFn: () => tagApi.getTags(),
    refetchOnWindowFocus: false,
  });
};
