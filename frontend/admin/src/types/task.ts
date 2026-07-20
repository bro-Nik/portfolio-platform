export interface Task {
  id: number;
  name: string;
  providerName: string;
  taskType: string;
  schedule: string;
  parameters: Record<string, any>;
  isActive: boolean;
  lastRun?: string;
  nextRun?: string;
  status?: string;
}

export interface TaskFormData {
  name: string;
  providerName: string;
  taskType: string;
  schedule: string;
  isActive: boolean;
  parameters: Record<string, any>;
}

export type CreateTaskData = TaskFormData;
export type UpdateTaskData = Partial<TaskFormData>;
