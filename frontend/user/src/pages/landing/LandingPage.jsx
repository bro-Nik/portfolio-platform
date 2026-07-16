import Header from './components/Header';
import heroBanner from './images/hero-banner.jpg';
import { Coins, TrendingUp, Globe, Briefcase, Wallet, Star } from 'lucide-react';
import { Typography, Card, Layout } from 'antd';

const { Title, Paragraph, Text } = Typography;

const LandingPage = () => {
  return (
    <>
      <main style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
        <section style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Header />

          <section style={{ display: 'flex', flexWrap: 'wrap-reverse', justifyContent: 'center', alignItems: 'center', maxWidth: 1140, margin: '0 auto', padding: '0 16px', flex: 1, gap: 48 }}>

            <div style={{ flex: '1 1 300px', minWidth: 300 }}>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <Title level={2} style={{ textTransform: 'uppercase', marginBottom: 48, color: '#e5bb15' }}>
                  Отслеживай активы в одном месте
                </Title>
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
                <Title level={2} style={{ color: '#212529' }}>Portfolios помогает не запутаться в инвестициях</Title>  
                <Paragraph style={{ color: '#6c757d', marginBottom: 0 }}><b>Portfolios</b> позволяет вести учет по многим активам в одном личном кабинете, что позволяет ничего не растерять и не забыть.</Paragraph>
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', rowGap: 16, columnGap: 16 }}>
                  <Card size="small" style={{ flex: 1, minWidth: 180 }} bordered={false}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                      <div style={{ padding: 4, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1rem + .15vw)', borderRadius: '.375rem' }}>
                        <Coins size={20} color="white" />
                      </div>
                      <Title level={4} style={{ marginBottom: 0, color: '#212529' }}>Криптовалюта</Title>
                    </div>
                    <Paragraph style={{ color: '#6c757d', marginBottom: 0 }}>Ведение криптовалютных портфелей с различнами стратегиями управления.</Paragraph>
                  </Card>

                  <Card size="small" style={{ flex: 1, minWidth: 180 }} bordered={false}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                      <div style={{ padding: 4, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1rem + .15vw)', borderRadius: '.375rem' }}>
                        <TrendingUp size={20} color="white" />
                      </div>
                      <Title level={4} style={{ marginBottom: 0, color: '#212529' }}>Акции</Title>
                    </div>
                    <Paragraph style={{ color: '#6c757d', marginBottom: 0 }}>Ведение портфелей с акциями разделенных по своему усмотрению.</Paragraph>
                  </Card>

                  <Card size="small" style={{ flex: 1, minWidth: 180 }} bordered={false}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                      <div style={{ padding: 4, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1rem + .15vw)', borderRadius: '.375rem' }}>
                        <Globe size={20} color="white" />
                      </div>
                      <Title level={4} style={{ marginBottom: 0, color: '#212529' }}>Офлайн активы</Title>
                    </div>
                    <Paragraph style={{ color: '#6c757d', marginBottom: 0 }}>Ведение портфелей с офлайн активами.</Paragraph>
                  </Card>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section style={{ maxWidth: 1140, margin: '0 auto', padding: '48px 16px' }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', rowGap: 48, columnGap: 48, padding: '48px 0' }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                <div style={{ padding: 8, borderRadius: '.375rem', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1.3rem + .6vw)' }}>
                  <Briefcase size={28} color="white" />
                </div>
                <Title level={3} style={{ color: '#212529', marginBottom: 0 }}>Портфели</Title>
              </div>
              <Paragraph>Управление портфелями с цифровыми и другими активами. Собирайте портфели по вашей собственной стратегии, цели или другому принципу.</Paragraph>
              <ul style={{ paddingLeft: 20, marginBottom: 0 }}>
                <li><Text>неограниченное количество портфелей</Text></li>
                <li><Text>процентное соотношение между портфелями и активами</Text></li>
                <li><Text>уведомления по достижению цены</Text></li>
                <li><Text>история транзакций</Text></li>
              </ul>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                <div style={{ padding: 8, borderRadius: '.375rem', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1.3rem + .6vw)' }}>
                  <Wallet size={28} color="white" />
                </div>
                <Title level={3} style={{ color: '#212529', marginBottom: 0 }}>Кошельки</Title>
              </div>
              <Paragraph>Удобное управление всеми кошельками, где хранятся активы. Вы можете вести столько кошельков, сколько необходимо, например, сколько у вас есть в реальности и понимать, где именно лежит интересующий актив и в каком количестве.</Paragraph>
              <ul style={{ paddingLeft: 20, marginBottom: 0 }}>
                <li><Text>неограниченное количество кошельков</Text></li>
                <li><Text>список активов в кошельке</Text></li>
                <li><Text>статистика по свободным средствам</Text></li>
                <li><Text>статистика по средствам, зарезервированным на ордеры</Text></li>
              </ul>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                <div style={{ padding: 8, borderRadius: '.375rem', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffc107', backgroundImage: 'linear-gradient(180deg, rgba(255,255,255,.15), rgba(255,255,255,0))', fontSize: 'calc(1.3rem + .6vw)' }}>
                  <Star size={28} color="white" />
                </div>
                <Title level={3} style={{ color: '#212529', marginBottom: 0 }}>Списки отслеживания</Title>
              </div>
              <Paragraph>Не теряйте и отслеживайте интересующие вас активы.</Paragraph>
              <ul style={{ paddingLeft: 20, marginBottom: 0 }}>
                <li><Text>список избранных активов</Text></li>
                <li><Text>уведомления по достижению цены</Text></li>
              </ul>
            </div>
          </div>
        </section>
        <Layout.Footer style={{ color: '#fff', padding: '16px', backgroundColor: '#212529', textAlign: 'center' }}>
          <span>{new Date().getFullYear()} Portfolios</span>
        </Layout.Footer>
      </main>

    </>
  );

};

export default LandingPage;
