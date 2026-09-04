import { getMarket } from 'src/api';
import type {
  ListTickersMarketAdminTickersGetParams,
  TickerDetailResponse,
  TickerListResponse,
  TickerUpdateRequest,
} from 'src/api';

const market = getMarket();

export type TickerListParams = ListTickersMarketAdminTickersGetParams;

export const tickersApi = {
  list: (params?: TickerListParams): Promise<TickerListResponse> =>
    market.listTickersMarketAdminTickersGet(params),

  getById: (id: number): Promise<TickerDetailResponse> => market.getTickerMarketAdminTickersTickerIdGet(id),

  update: (id: number, data: TickerUpdateRequest): Promise<TickerDetailResponse> =>
    market.updateTickerMarketAdminTickersTickerIdPut(id, data),

  delete: (id: number): Promise<void> => market.deleteTickerMarketAdminTickersTickerIdDelete(id),

  merge: (sourceId: number, targetId: number): Promise<TickerDetailResponse> =>
    market.mergeTickersMarketAdminTickersMergePost({ sourceId, targetId }),
};
