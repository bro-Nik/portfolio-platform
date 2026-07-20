import { createApi } from '@portfolio/shared';
import { CreateTaskData, Task, UpdateTaskData } from '../../../types/task';

const baseUrl = `${process.env.REACT_APP_MARKET_SERVICE_URL}/admin/tasks`;
const api = createApi(baseUrl, { useAuth: true });

export const tasksApi = {
  getTasks: (): Promise<Task[]> => {
    return api.get('');
  },

  createTask: (data: CreateTaskData): Promise<Task> => {
    return api.post('', data);
  },

  updateTask: (id: number, data: UpdateTaskData): Promise<Task> => {
    return api.put(`/${id}`, data);
  },

  deleteTask: (id: number): Promise<void> => {
    return api.del(`/${id}`);
  },

  runTask: (id: number): Promise<{ message: string; task_id: number }> => {
    return api.post(`/${id}/run`);
  },
}
