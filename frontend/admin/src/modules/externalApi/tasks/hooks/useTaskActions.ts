import { useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksApi } from '../api';
import { CreateTaskData, Task, UpdateTaskData } from '../../../../types/task';
import { useNotifications } from '@portfolio/shared';

export const useTaskActions = () => {
  const queryClient = useQueryClient();
  const { error, success } = useNotifications();

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['tasks'] });

  const simpleMutation = (successMsg: string, errorMsg: string) => ({
    onSuccess: () => {
      success(successMsg);
      invalidate();
    },
    onError: (err: Error) => error(err?.message || errorMsg),
  });

  const createMut = useMutation({
    mutationFn: (data: CreateTaskData) => tasksApi.createTask(data),
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });
      const previous = queryClient.getQueryData<Task[]>(['tasks']);
      const optimisticId = `optimistic-${Date.now()}`;
      queryClient.setQueryData<Task[]>(['tasks'], (old: Task[] | undefined) => [
        ...(old || []),
        { ...data, id: optimisticId } as unknown as Task,
      ]);
      return { previous, optimisticId };
    },
    onSuccess: () => {
      success('Задача успешно создана');
    },
    onError: (err: Error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['tasks'], context.previous);
      }
      error(err?.message || 'Ошибка создания');
    },
    onSettled: () => invalidate(),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateTaskData }) => tasksApi.updateTask(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });
      const previous = queryClient.getQueryData<Task[]>(['tasks']);
      queryClient.setQueryData<Task[]>(['tasks'], (old: Task[] | undefined) =>
        old?.map((t: Task) => t.id === id ? { ...t, ...data } : t)
      );
      return { previous };
    },
    onSuccess: (serverTask, { id }) => {
      queryClient.setQueryData<Task[]>(['tasks'], (old: Task[] | undefined) =>
        old?.map((t: Task) => t.id === id ? serverTask : t)
      );
      success('Задача успешно обновлена');
    },
    onError: (err: Error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['tasks'], context.previous);
      }
      error(err?.message || 'Ошибка обновления');
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => tasksApi.deleteTask(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });
      const previous = queryClient.getQueryData<Task[]>(['tasks']);
      queryClient.setQueryData<Task[]>(['tasks'], (old: Task[] | undefined) =>
        old?.filter((t: Task) => t.id !== id)
      );
      return { previous };
    },
    onSuccess: () => success('Задача успешно удалена'),
    onError: (err: Error, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['tasks'], context.previous);
      }
      error(err?.message || 'Ошибка удаления');
    },
  });

  const runMut = useMutation({
    mutationFn: (id: number) => tasksApi.runTask(id),
    ...simpleMutation('Задача запущена', 'Ошибка запуска'),
  });

  return {
    createTask: (data: CreateTaskData) => createMut.mutate(data),
    updateTask: (id: number, data: UpdateTaskData) => updateMut.mutate({ id, data }),
    deleteTask: (id: number) => deleteMut.mutate(id),
    runTask: (id: number) => runMut.mutate(id),
    isCreating: createMut.isPending,
    isUpdating: updateMut.isPending,
    isDeleting: deleteMut.isPending,
    isRunning: runMut.isPending,
  };
};
