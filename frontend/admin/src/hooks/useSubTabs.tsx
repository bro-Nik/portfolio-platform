import { useEffect, useState } from 'react';
import { useHeaderExtra, SubTabsBar, SubTabItem } from '../utils/headerContext';

interface UseSubTabsOptions<T extends string> {
  tabs: SubTabItem[];
  defaultKey: T;
  storageKey?: string;
}

export const useSubTabs = <T extends string>({ tabs, defaultKey, storageKey }: UseSubTabsOptions<T>) => {
  const [activeTab, setActiveTab] = useState<T>(() => {
    if (storageKey) {
      try {
        const stored = localStorage.getItem(storageKey);
        if (stored) return stored as T;
      } catch {}
    }
    return defaultKey;
  });
  const { setHeaderExtra } = useHeaderExtra();

  const handleChange = (key: string) => {
    setActiveTab(key as T);
    if (storageKey) {
      localStorage.setItem(storageKey, key);
    }
  };

  useEffect(() => {
    setHeaderExtra(<SubTabsBar tabs={tabs} activeKey={activeTab} onChange={handleChange} />);
    return () => setHeaderExtra(null);
  }, [activeTab, setHeaderExtra, tabs]);

  return { activeTab, setActiveTab: handleChange };
};
