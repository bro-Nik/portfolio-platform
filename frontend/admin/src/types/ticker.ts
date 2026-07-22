export interface Ticker {
  id: number;
  name: string;
  symbol: string;
  image?: string;
  marketCapRank?: number;
  price: number;
  market: string;
  isActive: boolean;
  priceUpdatedBy?: string;
  updatedAt?: string;
  externalIds?: Array<{ providerName: string; externalId: string }>;
  identifiers?: Array<{ system: string; value: string }>;
}

export interface TickerUpdateData {
  name?: string;
  symbol?: string;
  isActive?: boolean;
}

export interface TickerListResponse {
  data: Ticker[];
  hasMore: boolean;
  total: number;
}
