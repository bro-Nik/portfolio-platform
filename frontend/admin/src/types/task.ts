export type { TaskResponse as Task } from 'src/api';

export interface TaskFormData {
  name: string;
  providerName: string;
  taskType: string;
  schedule: string;
  isActive: boolean;
  parameters: Record<string, unknown>;
}

export type CreateTaskData = TaskFormData;
export type UpdateTaskData = Partial<TaskFormData>;
