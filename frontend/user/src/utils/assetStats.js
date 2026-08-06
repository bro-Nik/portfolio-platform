export const calculatePortfolioAssetStats = (asset, price) => {
  const assetQuantity = Number(asset.quantity) || 0;
  const assetAmount = Number(asset.amount) || 0;
  const assetRealizedProfit = Number(asset.realizedProfit) || 0;
  const assetTotalInvested = Number(asset.totalInvested) || 0;
  const assetBuyOrders = Number(asset.buyOrders) || 0;

  const priceValue = Number(price);
  const hasPrice = !(price == null || isNaN(priceValue));
  const assetCostNow = hasPrice ? assetQuantity * priceValue : null;
  const assetInvested = Math.max(0, assetAmount);
  const hasBasis = assetInvested > 0 || assetRealizedProfit !== 0;
  const assetAveragePrice = hasBasis && assetQuantity > 0 ? assetInvested / assetQuantity : null;
  const assetProfit = hasBasis && hasPrice ? assetCostNow - assetInvested + assetRealizedProfit : null;

  return {
    costNow: assetCostNow,
    invested: assetInvested,
    averagePrice: assetAveragePrice,
    realizedProfit: assetRealizedProfit,
    totalInvested: assetTotalInvested || assetInvested,
    buyOrders: assetBuyOrders,
    profit: assetProfit,
    price: hasPrice ? priceValue : null,
    hasBasis,
    hasPrice,
  };
};

export const calculateWalletAssetStats = (asset, price) => {
  const assetQuantity = Number(asset.quantity) || 0;
  const assetBuyOrders = Number(asset.buyOrders) || 0;

  const priceValue = Number(price) || 0;
  const assetCostNow = assetQuantity * priceValue;

  return {
    costNow: assetCostNow,
    buyOrders: assetBuyOrders,
    price: priceValue,
  };
};
