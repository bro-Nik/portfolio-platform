import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { apiService } from '/app/src/services/api';

export const useDataStore = create(
  devtools(
    (set, get) => ({
      portfolios: [],
      wallets: [],
      wishlist: [],
      
      assetPrices: {},        // { assetId: price }
      assetInfo: {},        // { assetId: info }
      assetData: {},   // { assetId: детали, транзакции }
      uniqueAssets: new Set(), // Set для отслеживания уникальных активов
      lastPriceUpdate: null,
      
      // ДЕЙСТВИЯ ДЛЯ ПОРТФЕЛЕЙ
      setPortfolios: (portfolios) => {
        set({ portfolios });
        // Автоматически добавляем активы портфелей
        get().addAssets(portfolios);
      },
      
      addPortfolio: (portfolio) => {
        set(state => ({
          portfolios: [...(state.portfolios || []), portfolio]
        }));
        // Автоматически добавляем активы нового портфеля
        get().addAssets([portfolio]);
      },

      updatePortfolio: (portfolioToUpdate) => {
        set(state => ({
          portfolios: state.portfolios.map(portfolio =>
            portfolio.id === portfolioToUpdate.id ? { ...portfolio, ...portfolioToUpdate } : portfolio
          )
        }));
      },
      
      deletePortfolio: (portfolioId) => {
        set(state => ({
          portfolios: state.portfolios.filter(
            portfolio => portfolio.id !== portfolioId
          )
        }));
      },
 
      // === ДЕЙСТВИЯ ДЛЯ КОШЕЛЬКОВ ===
      setWallets: (wallets) => {
        set({ wallets });
        // Автоматически добавляем активы кошельков
        get().addAssets(wallets);
      },
      
      addWallet: (wallet) => {
        set(state => ({
          wallets: [...state.wallets || [], wallet]
        }));
        // Автоматически добавляем активы кошелька
        get().addAssets([wallet]);
      },

      updateWallet: (walletId, updatedData) => {
        set(state => ({
          wallets: state.wallets.map(wallet =>
            wallet.id === walletId ? { ...wallet, ...updatedData } : wallet
          )
        }));
      },

      deleteWallet: (walletId) => {
        set(state => ({
          wallets: state.wallets.filter(
            wallet => wallet.id !== walletId
          )
        }));
      },

      // === ДЕЙСТВИЯ ДЛЯ АКТИВОВ ===
      addAssets: (assetsData) => {
        const assetIds = extractUniqueAssets(assetsData);
        const { uniqueAssets } = get();
        
        // Добавляем только новые активы
        const newAssetIds = assetIds.filter(id => !uniqueAssets.has(id));
        if (newAssetIds.length === 0) return;

        // Добавляем новые активы в uniqueAssets
        set(state => {
          const newUniqueAssets = new Set([...state.uniqueAssets, ...newAssetIds]);
          return { uniqueAssets: newUniqueAssets };
        });
        
        // Загружаем цены для новых активов
        console.log('Загружаем цены для новых активов');
        get().fetchAssetPrices(newAssetIds);

        // Загружаем информацию для новых активов
        get().fetchAssetInfo(newAssetIds);
      },
      
      fetchAssetPrices: async (assetIds = null) => {
        const ids = assetIds || Array.from(get().uniqueAssets);
        if (ids.length === 0) return;
        
        try {
          const api = apiService('/market/api/tickers');
          const result = await api.post('/prices', ids);
          
          if (result.success) {
            set(state => ({
              assetPrices: { ...state.assetPrices, ...result.data.prices },
              lastPriceUpdate: new Date().toISOString()
            }));
          }
        } catch (err) {
          console.warn('Ошибка загрузки цен:', err);
        }
      },

      fetchAssetInfo: async (assetIds) => {
        if (assetIds.length === 0) return;
        const ids = assetIds || Array.from(get().uniqueAssets);
        if (ids.length === 0) return;
        
        try {
          const api = apiService('/market/api/tickers');
          const result = await api.post('/info', ids);
          
          if (result.success) {
            set(state => ({
              assetInfo: { ...state.assetInfo, ...result.data.info },
            }));
          }
        } catch (err) {
          console.warn('Ошибка загрузки информации:', err);
        }
      },

      addAssetData: (assetId, data) => {
        set(state => {
          return {
            assetData: {
              ...state.assetData,
              [assetId]: data
            }
          };
        });
      },

      // Очистка данных активов для переданных assetIds
      clearAssetData: (assetIds) => {
        set(state => {
          const updatedAssetData = { ...state.assetData };
          
          assetIds.forEach(assetId => {
            delete updatedAssetData[assetId];
          });
          
          return { assetData: updatedAssetData };
        });
      },

      // Обновление активов портфелей
      updatePortfolioAssets: (portfolioAssets) => {
        set(state => {
          const updatedPortfolios = state.portfolios.map(portfolio => {
            // Находим активы, которые принадлежат этому портфелю
            const portfolioAssetsToUpdate = portfolioAssets.filter(
              asset => asset.portfolioId === portfolio.id
            );
            
            if (portfolioAssetsToUpdate.length === 0) {
              return portfolio;
            }
            
            // Обновляем или добавляем активы в портфель
            const updatedAssets = [...(portfolio.assets || [])];
            
            portfolioAssetsToUpdate.forEach(updatedAsset => {
              const existingIndex = updatedAssets.findIndex(
                asset => asset.id === updatedAsset.id
              );
              
              if (existingIndex >= 0) {
                // Обновляем существующий актив
                updatedAssets[existingIndex] = {
                  ...updatedAssets[existingIndex],
                  ...updatedAsset
                };
              } else {
                // Добавляем новый актив
                updatedAssets.push(updatedAsset);
              }
            });
            
            return {
              ...portfolio,
              assets: updatedAssets
            };
          });
          
          return { portfolios: updatedPortfolios };
        });
        
        // Добавляем тикеры
        const tickerIds = portfolioAssets.map(asset => asset.tickerId);
        get().addAssets({ tickerIds });

        // Очищаем кэш данных для обновленных активов
        const assetIds = portfolioAssets.map(asset => `p-${asset.id}`);
        get().clearAssetData(assetIds);
      },
      
      // Обновление активов кошельков
      updateWalletAssets: (walletAssets) => {
        set(state => {
          const updatedWallets = state.wallets.map(wallet => {
            // Находим активы, которые принадлежат этому кошельку
            const walletAssetsToUpdate = walletAssets.filter(
              asset => asset.walletId === wallet.id
            );
            
            if (walletAssetsToUpdate.length === 0) {
              return wallet;
            }
            
            // Обновляем или добавляем активы в кошелек
            const updatedAssets = [...(wallet.assets || [])];
            
            walletAssetsToUpdate.forEach(updatedAsset => {
              const existingIndex = updatedAssets.findIndex(
                asset => asset.id === updatedAsset.id
              );
              
              if (existingIndex >= 0) {
                // Обновляем существующий актив
                updatedAssets[existingIndex] = {
                  ...updatedAssets[existingIndex],
                  ...updatedAsset
                };
              } else {
                // Добавляем новый актив
                updatedAssets.push(updatedAsset);
              }
            });
            
            return {
              ...wallet,
              assets: updatedAssets
            };
          });
          
          return { wallets: updatedWallets };
        });
        
        // Добавляем тикеры
        const tickerIds = walletAssets.map(asset => asset.tickerId);
        get().addAssets({ tickerIds });

        // Очищаем кэш данных для обновленных активов
        const assetIds = walletAssets.map(asset => `w-${asset.id}`);
        get().clearAssetData(assetIds);
      },
      
    }),
    { name: 'Data Store' }
  )
);

// Вспомогательная функция
const extractUniqueAssets = (data) => {
  const assetSet = new Set();
  
  const processItem = (item) => {
    if (item.assets) {
      item.assets.forEach(asset => {
        if (asset.tickerId) assetSet.add(asset.tickerId);
      });
    } else if (item.tickerIds) {
      item.tickerIds.forEach(tickerId => {
        assetSet.add(tickerId);
      });
    }
    if (item.portfolios) item.portfolios.forEach(processItem);
    if (item.wishlist) item.wishlist.forEach(processItem);
  };

  if (Array.isArray(data)) {
    data.forEach(processItem);
  } else {
    processItem(data);
  }
  
  return Array.from(assetSet);
};
