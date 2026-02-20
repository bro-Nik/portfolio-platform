import { ROUTES } from '/app/src/constants/routes';
import { useAuthStore } from '/app/src/stores/authStore';

const Header = () => {
  const { user, loading, isAuthenticated } = useAuthStore();

  return (
    <header className="d-flex py-3 container">
      <div className="d-flex align-items-center">
        <img className="mb-0 me-2" src="/favicon.png" alt="" width="32" height="32" />
        <span className="fs-4">Portfolios</span>
      </div>


      {!loading && (
        <div className="d-flex align-items-center ms-auto gap-3 text-nowrap">
          <div>
            <select className="form-select border-0 fw-medium">
              <option selected value={'ru'}>RU</option>
            </select>
          </div>

          {isAuthenticated && (
            <a className="text-decoration-none text-capitalize fw-medium" href={ROUTES.APP}>{ user?.login }</a>
          )}

          {!isAuthenticated && (
            <>
              <a href={ROUTES.LOGIN} className="text-decoration-none fw-medium">Вход</a>
              <a href={ROUTES.DEMO} className="text-decoration-none fw-medium">Демо</a>
            </>
          )}

        </div>
      )}
    </header>
  );
};

export default Header;
