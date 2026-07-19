import { memo } from 'react';
import EmptyState from 'src/components/EmptyState';
import WalletHeader from './WalletHeader';
import WalletStatistic from './WalletStatistic';
import WalletTable from './WalletTable';
import { Coins } from 'lucide-react';

const WalletPage = memo(({ wallet, onRefresh }) => {

  if (!wallet.assets?.length) {
    return (
      <>
        <WalletHeader wallet={wallet} onRefresh={onRefresh} />
        <EmptyState
          icon={Coins}
          title="В кошельке пока нет активов"
          description="Здесь будут отображаться активы кошелька"
        />
      </>
    );
  }

  return (
    <>
      <WalletHeader wallet={wallet} onRefresh={onRefresh} />
      <WalletStatistic wallet={wallet} />
      <WalletTable wallet={wallet} assets={wallet.assets} onRefresh={onRefresh} />
    </>
  );
});

export default WalletPage;
