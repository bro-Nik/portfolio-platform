import { Provider } from "./provider";

export interface Task {
  id: number;
  name: string;
  providerId: number;
  providerName?: string;
  taskType: string;
  schedule: string;
  parameters: Record<string, any>;
  isActive: boolean;
  lastRun?: string;
  nextRun?: string;
  status?: string;
  provider?: Provider
}

export interface TaskFormData {
  name: string;
  providerId: number;
  taskType: string;
  schedule: string;
  isActive: boolean;
  parameters: Record<string, any>;
}

export type CreateTaskData = TaskFormData;
export type UpdateTaskData = Partial<TaskFormData>;
