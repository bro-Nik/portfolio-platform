import React from 'react';
import { ApiOutlined, TeamOutlined } from '@ant-design/icons';
import { SubTabItem } from '../../utils/headerContext';
import { useSubTabs } from '../../hooks/useSubTabs';
import { ProvidersModule } from './providers/ProvidersModule';
import { TasksModule } from './tasks/TasksModule';

type SubTabKey = 'providers' | 'tasks';

const tabs: SubTabItem[] = [
  { key: 'providers', label: 'API Провайдеры', icon: <ApiOutlined /> },
  { key: 'tasks', label: 'Задачи', icon: <TeamOutlined /> },
];

const components: Record<SubTabKey, React.FC> = {
  providers: ProvidersModule,
  tasks: TasksModule,
};

export const ExternalApiModule: React.FC = () => {
  const { activeTab } = useSubTabs({ tabs: tabs, defaultKey: 'providers', storageKey: 'subtab_externalApi' });

  const ActiveComponent = components[activeTab];
  return <ActiveComponent />;
};
