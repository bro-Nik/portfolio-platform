import { useQuery } from '@tanstack/react-query';
import { providersApi } from '../api';

export const useProviders = () => {
  return useQuery({
    queryKey: ['providers'],
    queryFn: () => providersApi.getProviders(),
  });
};

export const useProvidersWithMethods = () => {
  return useQuery({
    queryKey: ['providersWithMethods'],
    queryFn: () => providersApi.getProvidersWithMethods(),
  });
};
