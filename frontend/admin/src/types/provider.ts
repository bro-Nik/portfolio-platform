export type {
  ProviderLog,
  ProviderMethodsItem as ProviderWithMethods,
  ProviderMethodInfo as ProviderMethod,
  ProviderResponse as Provider,
  ProviderSettingsItem as ProviderPreset,
  ProviderStats,
} from 'src/api';

export interface ParameterSchemaField {
  name: string;
  label: string;
  type: 'string' | 'number' | 'select' | 'boolean';
  options?: Record<string, string>;
  required?: boolean;
  default?: unknown;
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
