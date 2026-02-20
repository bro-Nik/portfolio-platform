import WalletHeader from './WalletHeader';
import WalletStatistic from './WalletStatistic';
import WalletTable from './WalletTable';

const WalletPage = ({ wallet }) => {

  return (
    <>
      <WalletHeader wallet={wallet} />
      <WalletStatistic wallet={wallet} />
      <WalletTable wallet={wallet} assets={wallet.assets} />
    </>
  );
};

export default WalletPage;
