import React, { useState } from 'react';
import { Layout, Menu, Space, Typography, Avatar, Dropdown, Button } from 'antd';
import type { MenuProps } from 'antd';
import {
  SettingOutlined,
  UserOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  BellOutlined,
  LogoutOutlined,
  ApiOutlined,
  TeamOutlined,
  SunOutlined,
  MoonOutlined,
  StockOutlined
} from '@ant-design/icons';
import { useAuthStore, useModalStore, authService, useThemeStore, usePersistedState } from '@portfolio/shared';
import { ExternalApiModule } from './modules/externalApi/ExternalApiModule';
import { TickersModule } from './modules/tickers/TickersModule';
import { UsersModule } from './modules/users/UsersModule';
import { HeaderContext, useHeaderExtra, SubTabsBar } from './utils/headerContext';

type MenuKey = 'api-services' | 'users' | 'tickers';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const ModalContainer = (): React.ReactElement | null => {
  const { currentModal: ModalComponent, modalProps } = useModalStore();
  if (ModalComponent) return <ModalComponent {...modalProps} />;
  return null;
};

export { useHeaderExtra, SubTabsBar };
export type { SubTabItem } from './utils/headerContext';

const AdminPage = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout: storeLogout } = useAuthStore();
  const { logout } = authService();
  const { theme, toggleTheme } = useThemeStore();
  const [selectedMenu, setSelectedMenu] = usePersistedState<MenuKey>('lastPage', 'api-services');
  const [headerExtra, setHeaderExtra] = useState<React.ReactNode>(null);

  const setPage = (key: MenuKey): void => {
    setSelectedMenu(key);
    setHeaderExtra(null);
  };

  const handleLogout = async (): Promise<void> => {
    await logout();
    storeLogout();
  };

  const sidebarMenu = [
    { key: 'api-services', icon: <ApiOutlined />, label: 'API Сервисы' },
    { key: 'tickers', icon: <StockOutlined />, label: 'Тикеры' },
    { key: 'users', icon: <TeamOutlined />, label: 'Пользователи' },
  ];

  const userMenu: MenuProps['items'] = [
    { key: 'profile', label: 'Профиль', icon: <UserOutlined />, disabled: true },
    { key: 'settings', label: 'Настройки', icon: <SettingOutlined />, disabled: true },
    { type: 'divider' },
    { key: 'logout', label: 'Выйти', icon: <LogoutOutlined />, danger: true, onClick: handleLogout },
  ];

  const currentModuleLabel = sidebarMenu.find(item => item.key === selectedMenu)?.label || '';

  const renderContent = () => {
    switch (selectedMenu) {
      case 'api-services':
        return <ExternalApiModule />;
      case 'tickers':
        return <TickersModule />;
      case 'users':
        return <UsersModule />;
      default:
        return <ExternalApiModule />;
    }
  };

  return (
    <HeaderContext.Provider value={{ setHeaderExtra }}>
      <Layout className="admin-layout">
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          theme={theme === 'dark' ? 'dark' : 'light'}
          width={250}
        >
          <div className="admin-sider-header">
            <Space orientation="vertical" size="small">
              <Avatar size={collapsed ? 32 : 48} src="/favicon.png" shape="square" />
              {!collapsed && (
                <>
                  <Title level={5} style={{ margin: 0 }}>Portfolios Admin</Title>
                  <Typography.Text type="secondary">Панель управления</Typography.Text>
                </>
              )}
            </Space>
          </div>

          <Menu
            theme={theme === 'dark' ? 'dark' : 'light'}
            mode="inline"
            selectedKeys={[selectedMenu]}
            items={sidebarMenu}
            onSelect={({ key }) => setPage(key as MenuKey)}
            style={{ borderRight: 0, marginTop: '16px' }}
          />
        </Sider>

        <Layout>
          <Header className="admin-header">
            <Space align="center">
              <Button
                type="text"
                icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                onClick={() => setCollapsed(!collapsed)}
              />
              {currentModuleLabel}
              {headerExtra}
            </Space>

            <Space size="large">
              <Button type="text" icon={<BellOutlined />} shape="circle" />
              <Button
                type="text"
                icon={theme === 'dark' ? <SunOutlined /> : <MoonOutlined />}
                onClick={toggleTheme}
                title={theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'}
              />
              <Dropdown menu={{ items: userMenu }} placement="bottomRight">
                <Space style={{ cursor: 'pointer' }}>
                  <Avatar icon={<UserOutlined />} />
                  {!collapsed && <Typography.Text strong>{user?.login}</Typography.Text>}
                </Space>
              </Dropdown>
            </Space>
          </Header>

          <Content className="admin-content">
            {renderContent()}
          </Content>
        </Layout>
        <ModalContainer />
      </Layout>
    </HeaderContext.Provider>
  );
};

export default AdminPage;
