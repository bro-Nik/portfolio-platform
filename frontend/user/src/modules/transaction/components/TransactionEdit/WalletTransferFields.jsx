import React from 'react';
import { Form } from 'antd';
import FormSelect from '/app/src/features/forms/FormSelect';
import FormQuantityInput from '/app/src/features/forms/FormQuantityInput';

const WalletTransferFields = ({
  getWallets,
  fromWallet,
  baseTicker,
  isCounterTransaction,
}) => {
  const wallets = getWallets({ excludeId: fromWallet?.id, showTickerId: baseTicker?.id });

  return (
    <>
    {/* Кошелек отправитель */}
    <Form.Item name="walletId" hidden initialValue={fromWallet?.id}></Form.Item>

    {/* Кошелек получатель */}
    <FormSelect
      name='wallet2Id'
      label='Кошелек получатель'
      rules={[{ required: true, message: 'Выберите кошелек' }]}
      hidden={isCounterTransaction}
      options={wallets}
      fieldNames={{label: 'name', value: 'id'}}
      optionRender={(o, { index }) => (<>
        {o.data.name}
        <span className='option-subtext'>({o.data.free} {baseTicker?.symbol})</span>
      </>)}
    />

    {/* Количество */}
    <FormQuantityInput
      showFree={true}
      walletFree={fromWallet?.baseAssetFree}
      ticker={baseTicker?.symbol}
    />
    </>
  );
};

export default WalletTransferFields;
