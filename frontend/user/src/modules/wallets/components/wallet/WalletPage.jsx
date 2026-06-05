import WalletHeader from './WalletHeader';
import WalletStatistic from './WalletStatistic';
import WalletTable from './WalletTable';

const WalletPage = ({ wallet, onRefresh }) => {

  return (
    <>
      <WalletHeader wallet={wallet} onRefresh={onRefresh} />
      <WalletStatistic wallet={wallet} />
      <WalletTable wallet={wallet} assets={wallet.assets} onRefresh={onRefresh} />
    </>
  );
};

export default WalletPage;
