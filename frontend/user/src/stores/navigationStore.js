import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const store = (set, get) => ({
  // Активный раздел
  activeSection: 'portfolios',

  // Структура открытых элементов
  openedItems: {
    portfolios: [], // Массив открытых портфелей с активами
    wallets: [],    // Массив открытых кошельков с активами  
    wishlist: []    // Массив избранного с уведомлениями
  },

  // Действия
  actions: {
    // Смена основного раздела
    setActiveSection: (section) => set({ activeSection: section }),

    // Универсальные методы для использования в компонентах
    openItem: (item, itemType, parentId = null) => {
      const section = getMainSectionByItemType(itemType);

      // Проверяем, не открыт ли уже
      if (!!get().actions.getItem(section, item.id, itemType, parentId)) {
        get().actions.toggleMinimizeItem(item.id, itemType, parentId);
        return;
      }

      if (parentId) {
        get().actions.openChildItem(section, item, itemType, parentId);
      } else {
        get().actions.openParentItem(section, item, itemType);
      }
    },
    
    closeItem: (itemId, itemType, parentId = null) => {
      const section = getMainSectionByItemType(itemType);

      // Находим элемент до закрытия
      const closingItem = get().actions.getItem(section, itemId, itemType, parentId);

      if (parentId) {
        get().actions.closeChildItem(section, itemId, itemType, parentId);
      } else {
        get().actions.closeParentItem(section, itemId, itemType);
      }

      // Если закрыли активный элемент, переключаемся
      if (get().activeSection === `${itemType}-${itemId}`) {
        set({ activeSection: closingItem.openFrom || section });
      }
    },

    toggleMinimizeItem: (itemId, itemType, parentId = null) => {
      const section = getMainSectionByItemType(itemType);

      if (parentId) {
        get().actions.toggleMinimizeChildItem(section, itemId, itemType, parentId);
      } else {
        get().actions.toggleMinimizeParentItem(section, itemId, itemType);
      }

      // Если закрыли активный элемент, переключаемся
      if (get().activeSection === `${itemType}-${itemId}`) {
        const item = get().actions.getItem(section, itemId, itemType, parentId);
        set({ activeSection: item.openFrom || section });
      } else {
        set({ activeSection: `${itemType}-${itemId}` });
      }
    },

    // Вспомогательные методы

    // Работаем с портфелем, кошельком или избранным (родителем)
    openParentItem: (section, item, itemType) => {
      set(state => {
        const sectionItems = [...state.openedItems[section]];
        
        const newItem = {
          id: item.id,
          name: item.name,
          type: itemType,
          isMinimized: false,
          openFrom: get().activeSection,
          openedAssets: []
        };

        return {
          openedItems: {
            ...state.openedItems,
            [section]: [...sectionItems, newItem]
          },
          activeSection: `${itemType}-${item.id}`
        };
      });

    },

    // Активы
    openChildItem: (section, item, itemType, parentId) => {
      
      set(state => {
        const sectionItems = [...state.openedItems[section]];
        const parentIndex = sectionItems.findIndex(i => i.id === parentId);
        if (parentIndex === -1) return state;

        const parent = { ...sectionItems[parentIndex] };
        const parentAssets = [...parent.openedAssets];

        const newAsset = {
          id: item.id,
          name: item.symbol,
          type: itemType,
          isMinimized: false,
          openFrom: get().activeSection,
          parentId
        };

        const updatedSectionItems = [...sectionItems];
        updatedSectionItems[parentIndex] = {
          ...parent,
          openedAssets: [...parentAssets, newAsset]
        };

        return {
          openedItems: {
            ...state.openedItems,
            [section]: updatedSectionItems
          },
          activeSection: `${itemType}-${item.id}`
        };
      });
    },

    // Закрываем родительский элемент
    closeParentItem: (section, itemId, itemType) => {
      set(state => {
        const sectionItems = [...state.openedItems[section]];

        return {
          openedItems: {
            ...state.openedItems,
            [section]: sectionItems.filter(item => item.id !== itemId)
          }
        };
      });
    },

    // Активы
    closeChildItem: (section, itemId, itemType, parentId) => {
      set(state => {
        const sectionItems = [...state.openedItems[section]];

        const parentIndex = sectionItems.findIndex(i => i.id === parentId);
        if (parentIndex === -1) return state;
        
        const parent = { ...sectionItems[parentIndex] };

        sectionItems[parentIndex] = {
          ...parent,
          openedAssets: parent.openedAssets.filter(a => a.id !== itemId)
        };       

        return {
          openedItems: {
            ...state.openedItems,
            [section]: sectionItems
          }
        };
      });
    },

    toggleMinimizeParentItem: (section, itemId, itemType) => {
      set(state => {
        const sectionItems = [...state.openedItems[section]];
        
        const itemIndex = sectionItems.findIndex(i => i.id === itemId);
        if (itemIndex === -1) return state;
        
        const item = sectionItems[itemIndex];
        const newSectionItems = [...sectionItems];
        newSectionItems[itemIndex] = {
          ...item,
          isMinimized: !item.isMinimized,
          openFrom: item.isMinimized ? get().activeSection : item.openFrom
        };

        return {
          openedItems: {
            ...state.openedItems,
            [section]: newSectionItems
          }
        };
      });
    },

    toggleMinimizeChildItem: (section, itemId, itemType, parentId) => {
      set(state => {
        const sectionItems = [...state.openedItems[section]];
        
        const parentIndex = sectionItems.findIndex(i => i.id === parentId);
        if (parentIndex === -1) return state;
        
        const parent = { ...sectionItems[parentIndex] };
        const assetIndex = parent.openedAssets.findIndex(a => a.id === itemId);
        if (assetIndex === -1) return state;
        
        const openedAssets = [...parent.openedAssets];
        openedAssets[assetIndex] = {
          ...openedAssets[assetIndex],
          isMinimized: !openedAssets[assetIndex].isMinimized,
          openFrom: openedAssets[assetIndex].isMinimized ? get().activeSection : openedAssets[assetIndex].openFrom
        };
        
        const newSectionItems = [...sectionItems];
        newSectionItems[parentIndex] = {
          ...parent,
          openedAssets
        };
        
        return {
          openedItems: {
            ...state.openedItems,
            [section]: newSectionItems
          }
        };
      });
    },

    getItem: (section, itemId, itemType, parentId = null) => {
      const state = get();
      if (!parentId) return state.openedItems[section].find(i => i.id === itemId);

      const parent = state.openedItems[section].find(i => i.id === parentId);
      return parent?.openedAssets.find(a => a.id === itemId);
    },

    // Для сайдбара
    getGroupedItems: () => {
      return get().openedItems;
    }
  }
});

const useNavigationStore = create(
  persist(store, {
    name: 'user-navigation',
    partialize: (state) => ({
      activeSection: state.activeSection,
      openedItems: state.openedItems,
    }),
  }),
);

const getMainSectionByItemType = (itemType) => {
  const type = itemType.split('_')[0];
  const sectionMap = {
    'portfolio': 'portfolios',
    'wallet': 'wallets',
    'wishlist': 'wishlist',
  };
  return sectionMap[type] || 'portfolios';
};

export default useNavigationStore;
