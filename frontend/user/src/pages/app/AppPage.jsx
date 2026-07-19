import React, { memo, Suspense } from 'react';
import Sidebar from './components/Sidebar';
import { useNavigation } from 'src/hooks/useNavigation';
import { useAuthStore, useModalStore } from '@portfolio/shared';
import './styles/App.css';
import PortfoliosPage from 'src/modules/portfolios/components/portfolio-list/PortfoliosPage'
import PortfolioPage from 'src/modules/portfolios/components/portfolio/PortfolioPage';
import PortfolioAssetPage from 'src/modules/portfolios/components/asset/AssetPage';
import WalletsPage from 'src/modules/wallets/components/wallet-list/WalletsPage'
import WalletPage from 'src/modules/wallets/components/wallet/WalletPage';
import WalletAssetPage from 'src/modules/wallets/components/asset/AssetPage';
import WishlistPage from './WishlistPage'
import SettingsPage from 'src/pages/settings/SettingsPage'

import { usePortfoliosData } from 'src/modules/portfolios/hooks/usePortfoliosData';
import { useWalletsData } from 'src/modules/wallets/hooks/useWalletsData';

const ModalContainer = () => {
  const { currentModal: ModalComponent, modalProps } = useModalStore();
  if (ModalComponent) return <ModalComponent {...modalProps} />;
};

const AppPage = () => {
  const { activeSection, openedItems } = useNavigation();
  const { allPortfolios, refresh: refreshPortfolios } = usePortfoliosData();
  const { allWallets, refresh: refreshWallets } = useWalletsData();

  const mainSections = {
    'portfolios': PortfoliosPage,
    'wallets': WalletsPage,
    'wishlist': WishlistPage,
    'settings': SettingsPage,
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
      const portfolioData = allPortfolios?.find(p => p.id === portfolio.id);
      if (!portfolioData) return;

      renderItems.push(
        <div key={`portfolio-${portfolio.id}`} style={{ display: activeSection === `portfolio-${portfolio.id}` ? '' : 'none' }}>
          <PortfolioPage portfolio={portfolioData} onRefresh={refreshPortfolios} />
        </div>
      );
      
      portfolio.openedAssets.forEach(asset => {
        const assetData = portfolioData.assets.find(a => a.id === asset.id);
        if (!assetData) return;

        renderItems.push(
          <div key={`portfolio_asset-${asset.id}`} style={{ display: activeSection === `portfolio_asset-${asset.id}` ? '' : 'none' }}>
            <PortfolioAssetPage portfolio={portfolioData} asset={assetData} />
          </div>
        );
      });
    });

    // Рендер кошельков и их активов
    openedItems.wallets.forEach(wallet => {
      const walletData = allWallets?.find(w => w.id === wallet.id);
      if (!walletData) return;

      renderItems.push(
        <div key={`wallet-${wallet.id}`} style={{ display: activeSection === `wallet-${wallet.id}` ? '' : 'none' }}>
          <WalletPage wallet={walletData} onRefresh={refreshWallets} />
        </div>
      );
      
      wallet.openedAssets.forEach(asset => {
        const assetData = walletData.assets.find(a => a.id === asset.id);
        if (!assetData) return;

        renderItems.push(
          <div key={`wallet_asset-${asset.id}`} style={{ display: activeSection === `wallet_asset-${asset.id}` ? '' : 'none' }}>
            <WalletAssetPage wallet={walletData} asset={assetData} />
          </div>
        );
      });
    });
    
    return renderItems;
  };

  return (
    <>
      <Sidebar />
      
      <div id="wrapper">
        <div id="content" style={{ padding: 48 }}>
          {renderMainSection()}
          {renderOpenedItems()}
        </div>
      </div>
      <ModalContainer />
    </>
  );
};

export default AppPage;
