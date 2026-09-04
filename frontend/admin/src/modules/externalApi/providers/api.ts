import { getMarket } from 'src/api';
import type {
  GetProviderLogsMarketAdminProvidersProviderNameLogsGetParams,
  ProviderCreateRequest,
  ProviderLog,
  ProviderMethodsItem,
  ProviderResponse,
  ProviderSettingsItem,
  ProviderStats,
  ProviderUpdateRequest,
} from 'src/api';

const market = getMarket();

export const providersApi = {
  getProviders: (): Promise<ProviderResponse[]> => market.getProvidersMarketAdminProvidersGet(),

  createProvider: (data: ProviderCreateRequest): Promise<ProviderResponse> =>
    market.createProviderMarketAdminProvidersPost(data),

  updateProvider: (name: string, data: ProviderUpdateRequest): Promise<ProviderResponse> =>
    market.updateProviderMarketAdminProvidersProviderNamePut(name, data),

  deleteProvider: (name: string): Promise<void> =>
    market.deleteProviderMarketAdminProvidersProviderNameDelete(name),

  resetCountersProvider: (name: string): Promise<void> =>
    market.resetCountersMarketAdminProvidersProviderNameResetCountersPost(name),

  getProviderLogs: (
    name: string,
    params?: GetProviderLogsMarketAdminProvidersProviderNameLogsGetParams,
  ): Promise<ProviderLog[]> => market.getProviderLogsMarketAdminProvidersProviderNameLogsGet(name, params),

  getProviderStats: (name: string): Promise<ProviderStats> =>
    market.getProviderStatsMarketAdminProvidersProviderNameStatsGet(name),

  getProvidersWithPresets: (): Promise<ProviderSettingsItem[]> =>
    market.getProvidersWithSettingsMarketAdminProvidersWithSettingsGet(),

  getProvidersWithMethods: (): Promise<ProviderMethodsItem[]> =>
    market.getProvidersWithMethodsMarketAdminProvidersWithMethodsGet(),
};
