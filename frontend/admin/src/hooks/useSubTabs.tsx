import { useEffect, useState } from 'react';
import { useHeaderExtra, SubTabsBar, SubTabItem } from '../utils/headerContext';

interface UseSubTabsOptions<T extends string> {
  tabs: SubTabItem[];
  defaultKey: T;
}

export const useSubTabs = <T extends string>({ tabs, defaultKey }: UseSubTabsOptions<T>) => {
  const [activeTab, setActiveTab] = useState<T>(defaultKey);
  const { setHeaderExtra } = useHeaderExtra();

  useEffect(() => {
    setHeaderExtra(<SubTabsBar tabs={tabs} activeKey={activeTab} onChange={(key) => setActiveTab(key as T)} />);
    return () => setHeaderExtra(null);
  }, [activeTab, setHeaderExtra, tabs]);

  return { activeTab, setActiveTab };
};
