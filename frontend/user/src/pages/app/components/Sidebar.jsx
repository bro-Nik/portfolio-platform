import React from 'react';
import { useAuthStore, authService } from '@portfolio/shared';
import { useNavigation } from 'src/hooks/useNavigation';
import { useNavigate } from 'react-router-dom';
import { Dropdown, Space, Avatar, Menu, Select } from 'antd';
import { User, Settings, LogOut, ChevronDown, Briefcase, Wallet, Star, X } from 'lucide-react';
import '../styles/Sidebar.scss';

const Sidebar = () => {
  const navigate = useNavigate();
  const { activeSection, setActiveSection, openedItems, openItem, closeItem } = useNavigation();
  const { user, logout: authLogout, isAdmin } = useAuthStore();
  const { logout } = authService();

  const menuItems = [
    { id: 'portfolios', label: 'Портфели', icon: <Briefcase size={16} style={{ marginRight: 8 }} /> },
    { id: 'wallets', label: 'Кошельки', icon: <Wallet size={16} style={{ marginRight: 8 }} /> },
    { id: 'wishlist', label: 'Избранное', icon: <Star size={16} style={{ marginRight: 8 }} /> },
  ];

  const handleLogout = async () => {
    await logout();
    authLogout();
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
            <Settings size={16} style={{ marginRight: 8 }} />
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
        <X size={14} />
      </button>
    </div>
  );
};

const LocaleSelectors = () => (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
    <Select
      size="small"
      variant="borderless"
      defaultValue="ru"
      suffixIcon={<ChevronDown size={14} />}
      options={[
        { value: 'ru', label: 'RU' },
        { value: 'en', label: 'EN' },
      ]}
    />
    <Select
      size="small"
      variant="borderless"
      defaultValue="USD"
      suffixIcon={<ChevronDown size={14} />}
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
      icon: <User size={16} />,
      label: 'Профиль',
      onClick: () => console.log('Профиль')
    },
    {
      key: 'settings',
      icon: <Settings size={16} />,
      label: 'Настройки',
      disabled: true,
      onClick: () => console.log('Настройки')
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogOut size={16} />,
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
      <Space style={{ color: 'rgba(0,0,0,0.45)', cursor: 'pointer' }}>
        <Avatar 
          size="small" 
          icon={<User size={16} />}
        />
        <span className="user-login" style={{ maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {user?.login || 'Гость'}
          <ChevronDown size={12} />
        </span>
      </Space>
    </Dropdown>
  );
};

const SidebarHeader = () => (
  <>
    <div className="header-box">
      <a href="/" className="home-link link-body-emphasis">
        <img style={{ marginRight: 8 }} src="/favicon.png" alt="Логотип" width="32" height="32" />
        <span style={{ fontSize: 'calc(1.275rem + .3vw)' }}>Portfolios</span>
      </a>
    </div>
    <hr />
  </>
);

export default Sidebar;
