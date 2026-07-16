import { useEffect } from 'react';
import { useShallow } from 'zustand/react/shallow';
import { useDataStore } from 'src/stores/dataStore';
import { portfolioApi } from '../api/portfolioApi';
import { useTicker } from 'src/hooks/useTicker';
import { sortTransactions } from 'src/modules/assets/utils/assetUtils'

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
      try {
        const transactions = await portfolioApi.getAssetTransactions(asset.id);
        const ticker = getTicker(asset.tickerId);
        const newAssetData = { 
          ...asset,
          share: portfolio.costNow > 0 ? (asset.costNow / portfolio.costNow) * 100 : 0,
          image: ticker.image,
          name: ticker.name,
          symbol: ticker.symbol,
          free: asset.quantity - asset.buyOrders,
          transactions: sortTransactions(transactions),
        };
        addAssetData(assetIdInData, newAssetData);
      } catch (error) {
        console.warn('Ошибка загрузки данных актива:', error);
      }
    };

    loadAssetData();
  }, [asset, assetData, portfolio, getTicker, addAssetData, assetIdInData]);

  return {
    loading: !assetData,
    assetData,
  };
};
