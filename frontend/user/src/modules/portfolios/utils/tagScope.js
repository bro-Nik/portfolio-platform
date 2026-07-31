export const TAG_SCOPES = ['portfolio', 'wallet', 'asset'];

const ENTITY_TYPE_TO_SCOPE = {
  portfolio: 'portfolio',
  wallet: 'wallet',
  portfolio_asset: 'asset',
  wallet_asset: 'asset',
};

export const getTagScope = (entityType) => ENTITY_TYPE_TO_SCOPE[entityType] || null;
