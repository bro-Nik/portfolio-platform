import React from 'react';
import { Form } from 'antd';
import FormSelect from '/app/src/features/forms/FormSelect';
import FormQuantityInput from '/app/src/features/forms/FormQuantityInput';
import { getTransactionTypeInfo } from '/app/src/modules/transaction/utils/type';

const PortfolioInOutFields = ({
  getWallets,
  baseTicker,
  portfolio,
  wallet,
  transactionType,
  handleWalletChange,
}) => {

  const { isSpend } = getTransactionTypeInfo(transactionType);
  const wallets = getWallets({ showTickerId: baseTicker?.id });

  return (
    <>
    {/* Портфель */}
    <Form.Item name="portfolioId" hidden initialValue={portfolio?.id}></Form.Item>

    {/* Кошелек */}
    <FormSelect
      name="walletId"
      label='Кошелек' 
      rules={[{ required: true, message: 'Выберите кошелек' }]}
      onChange={handleWalletChange}
      fieldNames={{label: 'name', value: 'id'}}
      options={wallets}
      optionRender={(o, { index }) => (<>
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
    />
    </>
  );
};

export default PortfolioInOutFields;
