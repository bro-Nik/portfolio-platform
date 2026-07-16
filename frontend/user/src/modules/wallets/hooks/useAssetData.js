import { useEffect } from 'react';
import { useShallow } from 'zustand/react/shallow';
import { useDataStore } from 'src/stores/dataStore';
import { walletApi } from '../api/walletApi';
import { useTicker } from 'src/hooks/useTicker';
import { sortTransactions } from 'src/modules/assets/utils/assetUtils'

export const useAssetData = (wallet, asset) => {
  const { getTicker } = useTicker();
  const addAssetData = useDataStore(state => state.addAssetData);

  const assetIdInData = `w-${asset.id}`; // префикс для разделения (портфели, кошельки)
  const assetData = useDataStore(
    useShallow(state => state.assetData[assetIdInData]) 
  );


  useEffect(() => {
    if (assetData) return;

    const loadAssetData = async () => {
      try {
        const transactions = await walletApi.getAssetTransactions(asset.id);
        const ticker = getTicker(asset.tickerId);
        const newAssetData = { 
          ...asset,
          share: wallet.costNow > 0 ? (asset.costNow / wallet.costNow) * 100 : 0,
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
  }, [asset, assetData, wallet, getTicker, addAssetData, assetIdInData]);

  return {
    loading: !assetData,
    assetData,
  };
};
