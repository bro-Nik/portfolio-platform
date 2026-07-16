import { useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksApi } from '../api';
import { CreateTaskData, UpdateTaskData } from '../../../../types/task';
import { errorNotification, successNotification } from '../../../../utils';

export const useTaskActions = () => {
  const queryClient = useQueryClient();

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['tasks'] });

  // Общая логика для всех мутаций
  const mutationOptions = (successMsg: string, errorMsg: string) => ({
    onSuccess: () => {
      successNotification(successMsg);
      invalidate();
    },
    onError: (error: Error) => errorNotification(error, errorMsg),
  });

  const createMut = useMutation({
    mutationFn: (data: CreateTaskData) => tasksApi.createTask(data),
    ...mutationOptions('Задача успешно создана', 'Ошибка создания'),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateTaskData }) => tasksApi.updateTask(id, data),
    ...mutationOptions('Задача успешно обновлена', 'Ошибка обновления'),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => tasksApi.deleteTask(id),
    ...mutationOptions('Задача успешно удалена', 'Ошибка удаления'),
  });

  return {
    createTask: (data: CreateTaskData) => createMut.mutate(data),
    updateTask: (id: number, data: UpdateTaskData) => updateMut.mutate({ id, data }),
    deleteTask: (id: number) => deleteMut.mutate(id),
    isCreating: createMut.isPending,
    isUpdating: updateMut.isPending,
    isDeleting: deleteMut.isPending,
  };
};



