import { getMarket } from 'src/api';
import type {
  RunTaskMarketAdminTasksTaskIdRunPost202,
  TaskCreateRequest,
  TaskResponse,
  TaskUpdateRequest,
} from 'src/api';

const market = getMarket();

export const tasksApi = {
  getTasks: (): Promise<TaskResponse[]> => market.getTasksMarketAdminTasksGet(),

  createTask: (data: TaskCreateRequest): Promise<TaskResponse> => market.createTaskMarketAdminTasksPost(data),

  updateTask: (id: number, data: TaskUpdateRequest): Promise<TaskResponse> =>
    market.updateTaskMarketAdminTasksTaskIdPut(id, data),

  deleteTask: (id: number): Promise<void> => market.deleteTaskMarketAdminTasksTaskIdDelete(id),

  runTask: (id: number): Promise<RunTaskMarketAdminTasksTaskIdRunPost202> =>
    market.runTaskMarketAdminTasksTaskIdRunPost(id),
};

