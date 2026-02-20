import { useEffect } from 'react';
import { useShallow } from 'zustand/react/shallow';
import { useDataStore } from '/app/src/stores/dataStore';
import { portfolioApi } from '../api/portfolioApi';
import { useTicker } from '/app/src/hooks/useTicker';
import { sortTransactions } from '/app/src/modules/assets/utils/assetUtils'

export const useAssetData = (portfolio, asset) => {
  const { getTicker } = useTicker();
  const addAssetData = useDataStore(state => state.addAssetData);

  const assetIdInData = `p-${asset.id}`; // префикс для разделения (портфели, кошельки)
  const assetData = useDataStore(
    useShallow(state => state.assetData[assetIdInData]) 
  );

  useEffect(() => {
    if (assetData) return;

    const loadAssetData = async () => {
      const result = await portfolioApi.getAssetTransactions(asset.id);
      if (result.success) {
        const ticker = getTicker(asset.tickerId);
        const newAssetData = { 
          ...asset,
          // ...result.data,
          share: portfolio.costNow > 0 ? (asset.costNow / portfolio.costNow) * 100 : 0,
          image: ticker.image,
          name: ticker.name,
          symbol: ticker.symbol,
          free: asset.quantity - asset.buyOrders,
          transactions: sortTransactions(result.data),
        };
        addAssetData(assetIdInData, newAssetData);
      }
    };

    loadAssetData();
  }, [asset, assetData, portfolio, getTicker, addAssetData, assetIdInData]);

  return {
    loading: !assetData,
    assetData,
  };
};
