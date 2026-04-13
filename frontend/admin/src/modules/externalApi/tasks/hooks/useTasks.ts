import { useQuery } from '@tanstack/react-query';
import { tasksApi } from '../api';

export const useTasks = () => {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.getTasks(),
  });
};
