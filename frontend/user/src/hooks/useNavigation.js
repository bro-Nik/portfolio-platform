import useNavigationStore from '../stores/navigationStore';

export const useNavigation = () => {
  const { activeSection, openedItems, actions } = useNavigationStore();

  const {
    setActiveSection,
    openItem,
    closeItem,
    getGroupedItems,
    toggleMinimizeItem,
  } = actions;

  return {
    // Состояние
    activeSection,
    openedItems,
    
    // Геттеры
    groupedItems: getGroupedItems(),
    
    // Действия
    setActiveSection,
    openItem,
    closeItem,
    minimizeItem: toggleMinimizeItem,
    isSectionLoaded: (section) => openedItems[section]
  };
};
