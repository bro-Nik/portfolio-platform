import { useMemo, useState } from 'react';
import { useAuthStore, useThemeStore } from '@portfolio/shared';
import { useNavigation } from 'src/hooks/useNavigation';
import { useAuthMutations } from 'src/hooks/useAuthMutations';
import { usePreferencesStore } from 'src/stores/preferencesStore';
import { Dropdown, Space, Avatar, Select, Segmented } from 'antd';
import { User, Settings, ChevronDown, Briefcase, Wallet, Star, X, Sun, Moon, Monitor } from 'lucide-react';
import '../styles/Sidebar.scss';

const Sidebar = () => {
  const { activeSection, setActiveSection, openedItems, openItem, closeItem } = useNavigation();
  const { user, logout: authLogout, isAdmin } = useAuthStore();
  const { logout } = useAuthMutations();

  const menuItems = [
    { id: 'portfolios', label: 'Портфели', icon: <Briefcase size={16} style={{ marginRight: 8 }} /> },
    { id: 'wallets', label: 'Кошельки', icon: <Wallet size={16} style={{ marginRight: 8 }} /> },
    { id: 'wishlist', label: 'Избранное', icon: <Star size={16} style={{ marginRight: 8 }} /> },
  ];

  const handleLogout = async () => {
    await logout.mutateAsync();
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

const UserDropdown = ({ user, logout }) => {
  const { setActiveSection } = useNavigation();
  const { theme, setTheme } = useThemeStore();
  const { displayCurrency, rates, setCurrency } = usePreferencesStore();
  const [open, setOpen] = useState(false);

  const stopPropagation = (event) => event.stopPropagation();

  const currencyOptions = useMemo(() => {
    const symbols = Object.keys(rates).length > 0 ? Object.keys(rates) : ['USD', 'EUR', 'RUB'];
    return ['USD', ...symbols.filter(s => s !== 'USD')].map(symbol => ({ value: symbol, label: symbol }));
  }, [rates]);

  const menuItems = [
    {
      key: 'lang',
      label: (
        <div className="user-dropdown-row">
          <span className="user-dropdown-label" onClick={stopPropagation}>Язык</span>
          <Select
            size="small"
            variant="borderless"
            defaultValue="ru"
            onClick={stopPropagation}
            options={[
              { value: 'ru', label: 'RU' },
              { value: 'en', label: 'EN' },
            ]}
          />
        </div>
      ),
    },
    {
      key: 'currency',
      label: (
        <div className="user-dropdown-row">
          <span className="user-dropdown-label" onClick={stopPropagation}>Валюта</span>
          <Select
            size="small"
            variant="borderless"
            value={displayCurrency}
            onChange={setCurrency}
            onClick={stopPropagation}
            showSearch
            optionFilterProp="label"
            popupMatchSelectWidth={false}
            options={currencyOptions}
          />
        </div>
      ),
    },
    {
      key: 'theme',
      label: (
        <div className="user-dropdown-row">
          <span className="user-dropdown-label" onClick={stopPropagation}>Тема</span>
          <Segmented
            size="small"
            value={theme}
            shape="round"
            onChange={setTheme}
            onClick={stopPropagation}
            options={[
              { value: 'light', icon: <Sun size={14} />, tooltip: 'Светлая' },
              { value: 'dark', icon: <Moon size={14} />, tooltip: 'Тёмная' },
              { value: 'system', icon: <Monitor size={14} />, tooltip: 'Системная' },
            ]}
          />
        </div>
      ),
    },
    {
      type: 'divider',
    },
    {
      key: 'settings',
      label: 'Профиль',
      onClick: () => setActiveSection('settings')
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      label: 'Выход',
      danger: true,
      onClick: logout
    }
  ];

  return (
    <Dropdown
      open={open}
      onOpenChange={setOpen}
      menu={{ items: menuItems, className: 'user-dropdown-menu' }}
      trigger={['click']}
      placement="topRight"
      arrow
    >
      <Space style={{ color: 'var(--text-muted)', cursor: 'pointer' }}>
        <Avatar 
          size="small" 
          className="user-avatar"
          icon={<User size={16} />}
        />
        <span className="user-login" style={{ maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {user?.login || 'Гость'}
        </span>
        <ChevronDown size={14} style={{ color: 'var(--text-muted-icon)', display: 'flex', alignItems: 'center' }} />
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
