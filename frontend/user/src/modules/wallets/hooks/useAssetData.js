import { useEffect } from 'react';
import { useShallow } from 'zustand/react/shallow';
import { useDataStore } from '/app/src/stores/dataStore';
import { walletApi } from '../api/walletApi';
import { useTicker } from '/app/src/hooks/useTicker';
import { sortTransactions } from '/app/src/modules/assets/utils/assetUtils'

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
      const result = await walletApi.getAssetTransactions(asset.id);
      if (result.success) {
        const ticker = getTicker(asset.tickerId);
        const newAssetData = { 
          ...asset,
          // ...result.data,
          share: wallet.costNow > 0 ? (asset.costNow / wallet.costNow) * 100 : 0,
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
  }, [asset, assetData, wallet, getTicker, addAssetData, assetIdInData]);

  return {
    loading: !assetData,
    assetData,
  };
};
