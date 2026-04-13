import { createContext, useContext } from 'react';
import { Space, Button } from 'antd';

interface HeaderContextType {
  setHeaderExtra: (node: React.ReactNode) => void;
}

export const HeaderContext = createContext<HeaderContextType>({ setHeaderExtra: () => {} });

export const useHeaderExtra = () => useContext(HeaderContext);

export interface SubTabItem {
  key: string;
  label: string;
  icon: React.ReactNode;
}

interface SubTabsBarProps {
  tabs: SubTabItem[];
  activeKey: string;
  onChange: (key: string) => void;
}

export const SubTabsBar: React.FC<SubTabsBarProps> = ({ tabs, activeKey, onChange }) => (
  <Space size={4} style={{ marginLeft: '16px' }}>
    {tabs.map(tab => (
      <Button
        key={tab.key}
        type={activeKey === tab.key ? 'primary' : 'text'}
        icon={tab.icon}
        onClick={() => onChange(tab.key)}
        style={{
          borderRadius: '8px',
          fontWeight: activeKey === tab.key ? 600 : 400,
          borderColor: activeKey === tab.key ? undefined : 'transparent',
        }}
      >
        {tab.label}
      </Button>
    ))}
  </Space>
);
