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
  TeamOutlined
} from '@ant-design/icons';
import { useAuthStore, useModalStore, authService } from '@shared';
import { ExternalApiModule } from '/app/src/modules/externalApi/ExternalApiModule';
import { UsersModule } from '/app/src/modules/users/UsersModule';
import { HeaderContext, useHeaderExtra, SubTabsBar } from '/app/src/utils/headerContext';

type MenuKey = 'api-services' | 'users';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const ModalContainer = (): React.ReactElement | null => {
  const { currentModal: ModalComponent, modalProps } = useModalStore();
  if (ModalComponent) return <ModalComponent {...modalProps} />;
  return null;
};

export { useHeaderExtra, SubTabsBar };
export type { SubTabItem } from '/app/src/utils/headerContext';

const AdminPage = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedMenu, setSelectedMenu] = useState<MenuKey>((localStorage.getItem('lastPage') as MenuKey) || 'api-services');
  const [headerExtra, setHeaderExtra] = useState<React.ReactNode>(null);
  const { user, logout: storeLogout } = useAuthStore();
  const { logout } = authService();

  const setPage = (key: MenuKey): void => {
    setSelectedMenu(key);
    setHeaderExtra(null);
    localStorage.setItem('lastPage', key);
  };

  const handleLogout = async (): Promise<void> => {
    await logout();
    storeLogout();
  };

  const sidebarMenu = [
    { key: 'api-services', icon: <ApiOutlined />, label: 'API Сервисы' },
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
      case 'users':
        return <UsersModule />;
      default:
        return <ExternalApiModule />;
    }
  };

  return (
    <HeaderContext.Provider value={{ setHeaderExtra }}>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          theme="light"
          width={250}
        >
          <div style={{ padding: '16px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
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
            theme="light"
            mode="inline"
            selectedKeys={[selectedMenu]}
            items={sidebarMenu}
            onSelect={({ key }) => setPage(key as MenuKey)}
            style={{ borderRight: 0, marginTop: '16px' }}
          />
        </Sider>

        <Layout>
          <Header style={{
            padding: '0 24px',
            background: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 1px 4px rgba(0, 21, 41, 0.08)'
          }}>
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
              <Dropdown menu={{ items: userMenu }} placement="bottomRight">
                <Space style={{ cursor: 'pointer' }}>
                  <Avatar icon={<UserOutlined />} />
                  {!collapsed && <Typography.Text strong>{user?.login}</Typography.Text>}
                </Space>
              </Dropdown>
            </Space>
          </Header>

          <Content style={{
            margin: '16px',
            padding: 24,
            background: '#fff',
            borderRadius: '8px',
            minHeight: 280
          }}>
            {renderContent()}
          </Content>
        </Layout>
        <ModalContainer />
      </Layout>
    </HeaderContext.Provider>
  );
};

export default AdminPage;
