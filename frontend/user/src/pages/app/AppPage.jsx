import React, { Suspense } from 'react';
import Sidebar from './components/Sidebar';
import { useNavigation } from '/app/src/hooks/useNavigation';
import { useAuthStore } from '/app/src/stores/authStore';
// import { usePriceSync } from '/app/src/hooks/usePriceSync';
import './styles/App.css';
import PortfoliosPage from '/app/src/modules/portfolios/components/portfolio-list/PortfoliosPage'
import PortfolioPage from '/app/src/modules/portfolios/components/portfolio/PortfolioPage';
import PortfolioAssetPage from '/app/src/modules/portfolios/components/asset/AssetPage';
import WalletsPage from '/app/src/modules/wallets/components/wallet-list/WalletsPage'
import WalletPage from '/app/src/modules/wallets/components/wallet/WalletPage';
import WalletAssetPage from '/app/src/modules/wallets/components/asset/AssetPage';
import WishlistPage from './WishlistPage'
import { useModalStore } from '/app/src/stores/modalStore';
import { usePortfoliosData } from '/app/src/modules/portfolios/hooks/usePortfoliosData';
import { useWalletsData } from '/app/src/modules/wallets/hooks/useWalletsData';

const ModalContainer = () => {
  const { currentModal: ModalComponent, modalProps } = useModalStore();
  if (ModalComponent) return <ModalComponent {...modalProps} />;
};

const AppPage = () => {
  const { activeSection, openedItems } = useNavigation();
  const { portfolios } = usePortfoliosData();
  const { wallets } = useWalletsData();

  const mainSections = {
    'portfolios': PortfoliosPage,
    'wallets': WalletsPage,
    'wishlist': WishlistPage,
  }

  // Рендер основных разделов
  const renderMainSection = () => {
    return Object.entries(mainSections).map(([sectionName, SectionComponent]) => (
      <div 
        key={sectionName} 
        style={{ display: activeSection === sectionName ? 'block' : 'none' }}
      >
        <Suspense>
          <SectionComponent />
        </Suspense>
      </div>
    ));
  };

  // Рендер всех открытых элементов
  const renderOpenedItems = () => {
    const renderItems = [];
    
    // Рендер портфелей и их активов
    openedItems.portfolios.forEach(portfolio => {
      const portfolioData = portfolios?.find(p => p.id === portfolio.id);
      if (!portfolioData) return;

      // Портфель
      if (activeSection === `portfolio-${portfolio.id}`) {
        renderItems.push(
          <PortfolioPage key={`portfolio-${portfolio.id}`} portfolio={portfolioData} />
        );
      }
      
      // Активы портфеля
      portfolio.openedAssets.forEach(asset => {
        const assetData = portfolioData.assets.find(a => a.id === asset.id);
        if (!assetData) return;

        if (activeSection === `portfolio_asset-${asset.id}`) {
          renderItems.push(
            <PortfolioAssetPage key={`asset-${asset.id}`} portfolio={portfolioData} asset={assetData} />
          );
        }
      });
    });

    // Рендер кошельков и их активов
    openedItems.wallets.forEach(wallet => {
      const walletData = wallets?.find(w => w.id === wallet.id);
      if (!walletData) return;

      // Кошелек
      if (activeSection === `wallet-${wallet.id}`) {
        renderItems.push(
          <WalletPage key={`wallet-${wallet.id}`} wallet={walletData} />
        );
      }
      
      // Активы кошелька
      wallet.openedAssets.forEach(asset => {
        const assetData = walletData.assets.find(a => a.id === asset.id);
        if (!assetData) return;

        if (activeSection === `wallet_asset-${asset.id}`) {
          renderItems.push(
            <WalletAssetPage key={`asset-${asset.id}`} wallet={walletData} asset={assetData} />
          );
        }
      });
    });
    
    return renderItems;
  };

  return (
    <>
      {/* {usePriceSync()} */}
      <Sidebar />
      
      <div id="wrapper">
        <div id="content" className="p-5">
          {renderMainSection()}
          {renderOpenedItems()}
        </div>
      </div>
      <ModalContainer />
    </>
  );
};

export default AppPage;
