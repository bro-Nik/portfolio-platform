export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface Provider {
  id: number;
  name: string;
  apiKey?: string;
  requestsPerMinute?: number;
  requestsPerHour?: number;
  requestsPerDay?: number;
  requestsPerMonth?: number;
  isActive: boolean;
  timeout: number;
  retryDelay: number;
  minuteCounter: number;
  hourCounter: number;
  dayCounter: number;
  monthCounter: number;
}

export interface ProviderStats {
  providerName: string;
  requestsToday: number;
  successfulToday: number;
  failedToday: number;
  avgResponseTime: number;
  minuteCounter: number;
  minuteLimit: number;
  hourCounter: number;
  hourLimit: number;
  dayCounter: number;
  dayLimit: number;
  monthCounter: number;
  monthLimit: number;
  utilizationPercent: Record<string, number>;
}

export interface ProviderLog {
  id: number;
  providerId: number;
  endpoint: string;
  method: string;
  statusCode?: number;
  responseTime?: number;
  wasSuccessful: boolean;
  errorMessage?: string;
  requestParams: Record<string, any>;
  taskId: number;
  createdAt: string;
}

export interface ProviderPreset {
  name: string;
  displayName: string;
  requestsPerMinute: number;
  requestsPerHour: number;
  requestsPerDay: number;
  requestsPerMonth: number;
  timeout: number;
}

export interface ProviderMethod {
  method: string;
  name: string;
  description?: string;
  exampleParams?: Record<string, any>;
}

export interface ProviderWithMethods extends Provider {
  methods: ProviderMethod[];
}

export interface ProviderFormData {
  name: string;
  apiKey?: string;
  requestsPerMinute?: number;
  requestsPerHour?: number;
  requestsPerDay?: number;
  requestsPerMonth?: number;
  timeout: number;
  retryDelay: number;
  isActive: boolean;
}

export type CreateProviderData = ProviderFormData;
export type UpdateProviderData = Partial<ProviderFormData>;
