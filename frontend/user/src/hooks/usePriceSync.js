import { useEffect } from 'react';
import { useAssetsStore } from '/app/src/stores/assetsStore';

export const usePriceSync = () => {
  const { uniqueAssets, fetchAssetPrices } = useAssetsStore();
  
  useEffect(() => {
    if (uniqueAssets.size === 0) return;
    
    // Первая загрузка
    fetchAssetPrices();
    
    // Интервальное обновление
    const interval = setInterval(() => {
      fetchAssetPrices();
    // }, 30000);
    }, 3000000);
    
    return () => clearInterval(interval);
  }, [uniqueAssets.size, fetchAssetPrices]);
};
