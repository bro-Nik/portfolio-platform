import React from 'react';
import { Form } from 'antd';
import WalletSelect from 'src/features/forms/WalletSelect';
import FormQuantityInput from 'src/features/forms/FormQuantityInput';
import { getTransactionTypeInfo } from 'src/modules/transaction/utils/type';

const PortfolioInOutFields = ({
  getWallets,
  baseTicker,
  portfolio,
  wallet,
  transactionType,
  handleWalletChange,
  onAddWallet,
}) => {

  const { isSpend } = getTransactionTypeInfo(transactionType);
  const form = Form.useFormInstance();
  const quantityValue = Form.useWatch('quantity', form);
  const wallets = getWallets({ showTickerId: baseTicker?.id });

  return (
    <>

    {/* Портфель */}
    <Form.Item name="portfolioId" hidden initialValue={portfolio?.id}>
      <input />
    </Form.Item>

    {/* Кошелек */}
    <WalletSelect
      name="walletId"
      label='Кошелек' 
      rules={[{ required: true, message: 'Выберите кошелек' }]}
      onChange={handleWalletChange}
      variant="filled"
      status={!wallet ? 'warning' : undefined}
      placeholder="Выберите кошелек"
      fieldNames={{label: 'name', value: 'id'}}
      options={wallets}
      onAddWallet={onAddWallet}
      optionRender={(o) => (<>
        {o.data.name}
        {o.data.free !== undefined ? <span className='option-subtext'>({o.data.free} {baseTicker?.symbol})</span> : null}
      </>)}
    />

    {/* Количество */}
    <FormQuantityInput
      showFree={isSpend}
      walletFree={wallet?.baseAssetFree}
      portfolioFree={portfolio?.baseAssetFree}
      ticker={baseTicker?.symbol}
      status={wallet && !quantityValue ? 'warning' : undefined}
    />
    </>
  );
};

export default PortfolioInOutFields;
