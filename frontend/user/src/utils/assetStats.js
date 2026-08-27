export const calculatePortfolioAssetStats = (asset, price) => {
  const assetQuantity = Number(asset.quantity) || 0;
  const assetAmount = Number(asset.amount) || 0;
  const assetRealizedProfit = Number(asset.realizedProfit) || 0;
  const assetTotalInvested = Number(asset.totalInvested) || 0;
  const assetBuyOrders = Number(asset.buyOrders) || 0;
  const assetSellOrders = Number(asset.sellOrders) || 0;

  const priceValue = Number(price);
  const hasPrice = !(price == null || isNaN(priceValue));
  const assetCostNow = hasPrice ? assetQuantity * priceValue : null;
  const assetInvested = Math.max(0, assetAmount);
  const hasBasis = assetInvested > 0 || assetRealizedProfit !== 0;
  const assetAveragePrice = hasBasis && assetQuantity > 0 ? assetInvested / assetQuantity : null;
  const assetProfit = hasBasis && hasPrice
    ? assetCostNow - assetInvested + assetRealizedProfit
    : (hasBasis && assetRealizedProfit !== 0 ? assetRealizedProfit : null);

  return {
    costNow: assetCostNow,
    invested: assetInvested,
    averagePrice: assetAveragePrice,
    realizedProfit: assetRealizedProfit,
    totalInvested: assetTotalInvested || assetInvested,
    buyOrders: assetBuyOrders,
    sellOrders: assetSellOrders,
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

const withShare = (items, total, getNumerator) => {
  if (total <= 0) return items;
  return items.map(item => ({
    ...item,
    share: (getNumerator(item) / total) * 100,
  }));
};

export const buildPortfolioStats = (rawPortfolios, prices) => {
  const portfolios = rawPortfolios || [];
  if (portfolios.length === 0) return { items: [], overall: {} };

  let totalCostNow = 0;
  let totalInvested = 0;
  let totalBuyOrders = 0;
  let totalProfit = 0;
  let totalCapitalDeployed = 0;

  const items = portfolios.map(portfolio => {
    let costNow = 0;
    let invested = 0;
    let buyOrders = 0;
    let profit = 0;
    let capitalDeployed = 0;

    const assetsWithStats = portfolio.assets?.map(asset => {
      const stats = calculatePortfolioAssetStats(asset, prices[asset.tickerId]);

      costNow += stats.costNow || 0;
      invested += stats.invested;
      buyOrders += stats.buyOrders;
      profit += stats.profit ?? 0;
      capitalDeployed += stats.totalInvested;

      return {
        ...asset,
        ...stats,
      };
    }) || [];

    totalCostNow += costNow;
    totalInvested += invested;
    totalBuyOrders += buyOrders;
    totalProfit += profit;
    totalCapitalDeployed += capitalDeployed;

    return {
      ...portfolio,
      assets: assetsWithStats,
      costNow,
      invested,
      totalInvested: capitalDeployed,
      buyOrders,
      profit,
    };
  });

  return {
    items: withShare(items, totalInvested, item => item.invested),
    overall: {
      totalCostNow,
      totalInvested,
      totalProfit,
      totalBuyOrders,
      totalCapitalDeployed,
    },
  };
};

export const buildWalletStats = (rawWallets, prices) => {
  const wallets = rawWallets || [];
  if (wallets.length === 0) return { items: [], overall: {} };

  let totalCostNow = 0;
  let totalBuyOrders = 0;

  const items = wallets.map(wallet => {
    let costNow = 0;
    let buyOrders = 0;

    const assetsWithStats = wallet.assets?.map(asset => {
      const stats = calculateWalletAssetStats(asset, prices[asset.tickerId] || 0);

      costNow += stats.costNow;
      buyOrders += stats.buyOrders;

      return {
        ...asset,
        ...stats,
      };
    }) || [];

    totalCostNow += costNow;
    totalBuyOrders += buyOrders;

    return {
      ...wallet,
      assets: assetsWithStats,
      costNow,
      buyOrders,
    };
  });

  return {
    items: withShare(items, totalCostNow, item => item.costNow),
    overall: {
      totalCostNow,
      totalBuyOrders,
    },
  };
};
