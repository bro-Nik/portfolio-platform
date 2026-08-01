import { useEffect } from 'react';
import { useHeaderExtra, SubTabsBar, SubTabItem } from '../utils/headerContext';
import { usePersistedState } from '@portfolio/shared';

interface UseSubTabsOptions<T extends string> {
  tabs: SubTabItem[];
  defaultKey: T;
  storageKey?: string;
}

export const useSubTabs = <T extends string>({ tabs, defaultKey, storageKey }: UseSubTabsOptions<T>) => {
  const [activeTab, setActiveTab] = usePersistedState<T>(storageKey, defaultKey);
  const { setHeaderExtra } = useHeaderExtra();

  useEffect(() => {
    setHeaderExtra(<SubTabsBar tabs={tabs} activeKey={activeTab} onChange={(key) => setActiveTab(key as T)} />);
    return () => setHeaderExtra(null);
  }, [activeTab, setHeaderExtra, tabs, setActiveTab]);

  return { activeTab, setActiveTab };
};
