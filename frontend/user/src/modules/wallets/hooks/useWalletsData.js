import { useEffect, useMemo, useRef } from 'react';
import { useDataStore } from 'src/stores/dataStore';
import { walletApi } from '../api/walletApi';

export const useWalletsData = () => {
  // Берем данные из единого store
  const wallets = useDataStore(state => state.wallets);
  const prices = useDataStore(state => state.assetPrices);
  const setWallets = useDataStore(state => state.setWallets);

  // Отслеживание первоначальной загрузки
  const initialLoadRef = useRef(false);

  const getWallet = (walletId) => {
    return wallets?.find(wallet => wallet.id === walletId) || null;
  };

  useEffect(() => {
    const fetchInitialData = async () => {
      initialLoadRef.current = true;
      try {
        const data = await walletApi.getAllWallets();
        setWallets(data.wallets || []);
      } catch (error) {
        console.warn('Ошибка загрузки кошельков:', error);
      }
    };

    // Загружаем только один раз
    if (wallets.length === 0 && !initialLoadRef.current) fetchInitialData();
  }, [setWallets, wallets.length]);

  // Расчет статистики
  const { walletsWithStats, overallStats } = useMemo(() => {
    if (wallets === null || wallets.length === 0) return { walletsWithStats: [], overallStats: {} };

    let totalCostNow = 0;
    let totalBuyOrders = 0;
    
    // Расчет статистики для каждого кошелька
    const walletsWithStats = wallets.map(wallet => {
      let costNow = 0;
      let buyOrders = 0;

      // Расчет статистики для каждого актива
      const assetsWithStats = wallet.assets?.map(asset => {
        const assetQuantity = Number(asset.quantity) || 0;
        const assetBuyOrders = Number(asset.buyOrders) || 0;

        const price = prices[asset.tickerId] || 0;
        const assetCostNow = assetQuantity * price;

        costNow += assetCostNow;
        buyOrders += assetBuyOrders || 0;

        return {
          ...asset,
          costNow: assetCostNow,
          price
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

    const walletsWithStatsAndShare = walletsWithStats.map(wallet => ({
      ...wallet,
      share: totalCostNow > 0 ? (wallet.costNow / totalCostNow) * 100 : 0
    }));

    return {
      walletsWithStats: walletsWithStatsAndShare,
      overallStats: {
        totalCostNow,
        totalBuyOrders
      }
    };
  }, [wallets, prices]);

  const refresh = async () => {
    try {
      const data = await walletApi.getAllWallets();
      setWallets(data.wallets || []);
    } catch (error) {
      console.warn('Ошибка обновления кошельков:', error);
    }
  };

  return {
    wallets: walletsWithStats,
    overallStats,
    loading: wallets === null,
    getWallet,
    refresh,
  };
};
