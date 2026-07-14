import Header from './components/Header';
import heroBanner from './images/hero-banner.jpg';
import { Coins, TrendingUp, Globe, Briefcase, Wallet, Star } from 'lucide-react';

const LandingPage = () => {
  return (
    <>
      <main style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
        <section style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Header />

          <section style={{ display: 'flex', flexWrap: 'wrap-reverse', justifyContent: 'center', alignItems: 'center', maxWidth: 1140, margin: '0 auto', padding: '0 48px', flex: 1, gap: 48 }}>

            <div style={{ flex: '1 1 300px', minWidth: 300 }}>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <h2 style={{ textTransform: 'uppercase', marginBottom: 48, fontWeight: 700, fontSize: 'calc(1.475rem + 2.7vw)', color: '#e5bb15' }}>
                  Отслеживай активы в одном месте
                </h2>
              </div>
            </div>

            <div style={{ flex: '1 1 400px', minWidth: 300 }}>
              <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', width: '100%' }}>
                <img src={heroBanner} alt="hero" style={{ width: '100%' }} />
              </div>
            </div>

          </section>

        </section>

        <section style={{ backgroundColor: '#e9ecef' }}>
          <div style={{ maxWidth: 1140, margin: '0 auto', padding: '0 16px' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', rowGap: 48, columnGap: 48, padding: '48px 0', alignItems: 'center' }}>
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 8 }}>
                <h2 style={{ fontWeight: 700, color: '#212529' }}>Portfolios помогает не запутаться в инвестициях</h2>  
                <p style={{ color: '#6c757d' }}><b>Portfolios</b> позволяет вести учет по многим активам в одном личном кабинете, что позволяет ничего не растерять и не забыть.</p>
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', rowGap: 16, columnGap: 16 }}>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ padding: 4, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1rem + .15vw)', borderRadius: '.375rem' }}>
                      <Coins size={20} color="white" />
                    </div>
                    <h4 style={{ fontWeight: 600, marginBottom: 0, color: '#212529' }}>Криптовалюта</h4>
                    <p style={{ color: '#6c757d' }}>Ведение криптовалютных портфелей с различнами стратегиями управления.</p>
                  </div>

                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ padding: 4, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1rem + .15vw)', borderRadius: '.375rem' }}>
                      <TrendingUp size={20} color="white" />
                    </div>
                    <h4 style={{ fontWeight: 600, marginBottom: 0, color: '#212529' }}>Акции</h4>
                    <p style={{ color: '#6c757d' }}>Ведение портфелей с акциями разделенных по своему усмотрению.</p>
                  </div>

                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ padding: 4, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1rem + .15vw)', borderRadius: '.375rem' }}>
                      <Globe size={20} color="white" />
                    </div>
                    <h4 style={{ fontWeight: 600, marginBottom: 0, color: '#212529' }}>Офлайн активы</h4>
                    <p style={{ color: '#6c757d' }}>Ведение портфелей с офлайн активами.</p>
                  </div>

                </div>
              </div>
            </div>
          </div>
        </section>

        <section style={{ maxWidth: 1140, margin: '0 auto', padding: '48px 16px' }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', rowGap: 48, columnGap: 48, padding: '48px 0' }}>
            <div style={{ flex: 1 }}>
              <div style={{ padding: 8, borderRadius: '.375rem', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1.3rem + .6vw)', marginBottom: 16 }}>
                <Briefcase size={28} color="white" />
              </div>
              <h3 style={{ fontSize: 'calc(1.3rem + .6vw)', color: '#212529' }}>Портфели</h3>
              <p>Управление портфелями с цифровыми и другими активами. Собирайте портфели по вашей собственной стратегии, цели или другому принципу.</p>
              <ul style={{ fontWeight: 300 }}>
                <li>неограниченное количество портфелей</li>
                <li>процентное соотношение между портфелями и активами</li>
                <li>уведомления по достижению цены</li>
                <li>история транзакций</li>
              </ul>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ padding: 8, borderRadius: '.375rem', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1.3rem + .6vw)', marginBottom: 16 }}>
                <Wallet size={28} color="white" />
              </div>
              <h3 style={{ fontSize: 'calc(1.3rem + .6vw)', color: '#212529' }}>Кошельки</h3>
              <p>Удобное управление всеми кошельками, где хранятся активы. Вы можете вести столько кошельков, сколько необходимо, например, сколько у вас есть в реальности и понимать, где именно лежит интересующий актив и в каком количестве.</p>
              <ul style={{ fontWeight: 300 }}>
                <li>неограниченное количество кошельков</li>
                <li>список активов в кошельке</li>
                <li>статистика по свободным средствам</li>
                <li>статистика по средствам, зарезервированным на ордеры</li>
              </ul>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ padding: 8, borderRadius: '.375rem', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1.3rem + .6vw)', marginBottom: 16 }}>
                <Star size={28} color="white" />
              </div>
              <h3 style={{ fontSize: 'calc(1.3rem + .6vw)', color: '#212529' }}>Списки отслеживания</h3>
              <p>Не теряйте и отслеживайте интересующие вас активы.</p>
              <ul style={{ fontWeight: 300 }}>
                <li>список избранных активов</li>
                <li>уведомления по достижению цены</li>
              </ul>
            </div>
          </div>
        </section>
        <footer style={{ display: 'flex', color: '#fff', marginTop: 'auto', padding: '16px 0', backgroundColor: '#212529', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', textAlign: 'center' }}>
          <span style={{ margin: '0 auto' }}>2025 Portfolios</span>
        </footer>
      </main>

    </>
  );

};

export default LandingPage;
