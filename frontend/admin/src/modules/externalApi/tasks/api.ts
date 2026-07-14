import { createApi } from '@shared';
import { CreateTaskData, Task, UpdateTaskData } from '/app/src/types/task';

const baseUrl = `${process.env.REACT_APP_MARKET_SERVICE_URL}/admin/tasks`;
const api = createApi(baseUrl, { convertCase: true, useAuth: true });

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
}
