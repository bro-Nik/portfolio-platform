import { ROUTES } from 'src/constants/routes';
import { useAuthStore } from '@portfolio/shared';
import { Select } from 'antd';

const Header = () => {
  const { user, loading, isAuthenticated } = useAuthStore();

  return (
    <header style={{ display: 'flex', padding: '16px', maxWidth: 1140, margin: '0 auto', width: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <img style={{ marginBottom: 0, marginRight: 8 }} src="/favicon.png" alt="" width="32" height="32" />
        <span style={{ fontSize: 'calc(1.275rem + .3vw)' }}>Portfolios</span>
      </div>

      {!loading && (
        <div style={{ display: 'flex', alignItems: 'center', marginLeft: 'auto', gap: 12, whiteSpace: 'nowrap' }}>
          <div>
            <Select
              size="small"
              variant="borderless"
              defaultValue="ru"
              style={{ fontWeight: 500 }}
              options={[
                { value: 'ru', label: 'RU' },
              ]}
            />
          </div>

          {isAuthenticated && (
            <a style={{ textDecoration: 'none', textTransform: 'capitalize', fontWeight: 500 }} href={ROUTES.APP}>{ user?.login }</a>
          )}

          {!isAuthenticated && (
            <>
              <a href={ROUTES.LOGIN} style={{ textDecoration: 'none', fontWeight: 500 }}>Вход</a>
            </>
          )}

        </div>
      )}
    </header>
  );
};

export default Header;
