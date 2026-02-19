import React from 'react';
import { useAuthStore } from '/app/src/stores/authStore';
import { useNavigation } from '/app/src/hooks/useNavigation';
import { useNavigate } from 'react-router-dom';
import { authService } from '/app/src/services/auth';
import { Dropdown, Space, Avatar, Menu, Select } from 'antd';
import { UserOutlined, SettingOutlined, LogoutOutlined, BellOutlined, DownOutlined } from '@ant-design/icons';
import { UserCircleIcon, ChevronDownIcon, UserIcon } from '@heroicons/react/16/solid'
import '../styles/Sidebar.scss';

const Sidebar = () => {
  const navigate = useNavigate();
  const { activeSection, setActiveSection, openedItems, openItem, closeItem } = useNavigation();
  const { user, logout: authLogout, isAdmin } = useAuthStore();
  const { logout } = authService();

  const menuItems = [
    { id: 'portfolios', label: 'Портфели', icon: <i className="bi bi-briefcase me-2" /> },
    { id: 'wallets', label: 'Кошельки', icon: <i className="bi bi-wallet me-2" /> },
    { id: 'wishlist', label: 'Избранное', icon: <i className="bi bi-star me-2" /> },
  ];

  const handleLogout = async () => {
    const result = await logout();
    
    if (result.success) {
      authLogout();
    } else {
      console.log(result.error);
    }
    
  };

  const renderItemGroup = (items, section) => {
    if (!items?.length) return null;

    return items.map(item => (
      <div key={`${section}-${item.id}`} className="section-group">
        <SidebarItem
          item={item}
          onClick={() => openItem(item, item.type)}
          onClose={() => closeItem(item.id, item.type)}
          activeSection={activeSection}
          isParent={true}
        />

        <div className="group-children-list">
          {item.openedAssets?.map(asset => (
            <SidebarItem
              key={`${asset.type}-${asset.id}`}
              item={asset}
              onClick={() => openItem(asset, asset.type, item.id)}
              onClose={() => closeItem(asset.id, asset.type, item.id)}
              activeSection={activeSection}
            />
          ))}
        </div>
      </div>
    ));
  };

  return (
    <div id="sidebar">
      <SidebarHeader />
      
      <nav className="menu">
        {menuItems.map(({ id, label, icon }) => (
          <div key={id} className="menu-section">
            <button
              className={`item section-parent ${ activeSection === id ? 'active' : ''}`}
              onClick={() => setActiveSection(id)}
            >
              {icon}
              {label}
            </button>
            
            {renderItemGroup(openedItems[id], id)}
          </div>
        ))}

        {/* Кнопка администратора */}
        {isAdmin() && (
          <button
            className='item section-parent'
            onClick={() => window.location.href = '/admin/'}
          >
            <i className="bi bi-gear me-2" />
            Админ
          </button>
        )}
      </nav>

      <div className="user-panel">
        <LocaleSelectors />
        <hr />
        <UserDropdown user={user} logout={handleLogout} />
      </div>
    </div>
  );
};

const SidebarItem = ({ item, onClick, onClose, activeSection, isParent = false }) => {
  const isActive = activeSection === `${item.type}-${item.id}`;
  const classPrefix = isParent ? 'parent' : 'children';
  
  return (
    <div className={`item group-${classPrefix} ${isActive ? 'active' : ''}`}>
      <button className={`group-${classPrefix}-name`} onClick={onClick} >
        {item.name}
      </button>
      <button className="item-close" onClick={onClose} title="Закрыть" >
        <i className="bi bi-x" />
      </button>
    </div>
  );
};

const LocaleSelectors = () => (
  <div className="d-flex align-items-center justify-content-between">
    <Select
      size="small"
      variant="borderless"
      defaultValue="ru"
      suffixIcon=<ChevronDownIcon />
      options={[
        { value: 'ru', label: 'RU' },
        { value: 'en', label: 'EN' },
      ]}
    />
    <Select
      size="small"
      variant="borderless"
      defaultValue="USD"
      suffixIcon=<ChevronDownIcon />
      options={[
        { value: 'USD', label: 'USD' },
        { value: 'EUR', label: 'EUR' },
        { value: 'RUB', label: 'RUB' },
      ]}
    />
  </div>
);

const UserDropdown = ({ user, logout }) => {
  const menuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Профиль',
      onClick: () => console.log('Профиль')
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Настройки',
      disabled: true,
      onClick: () => console.log('Настройки')
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Выход',
      danger: true,
      onClick: logout
    }
  ];

  return (
    <Dropdown
      menu={{ items: menuItems }}
      trigger={['click']}
      placement="topRight"
      arrow
    >
      <Space className="text-secondary" style={{ cursor: 'pointer' }}>
        <Avatar 
          size="small" 
          // icon={<UserCircleIcon />}
          icon={<UserIcon />}
        />
        <span className="user-login text-truncate" style={{ maxWidth: '120px' }}>
          {user?.login || 'Гость'}
          <ChevronDownIcon />
        </span>
      </Space>
    </Dropdown>
  );
};

const SidebarHeader = () => (
  <>
    <div className="header-box">
      <a href="/" className="home-link link-body-emphasis">
        <img className="me-2" src="/favicon.png" alt="Логотип" width="32" height="32" />
        <span className="fs-4">Portfolios</span>
      </a>
      <BellOutlined style={{ color: '#6c757d', cursor: 'pointer' }} />
    </div>
    <hr />
  </>
);

export default Sidebar;
