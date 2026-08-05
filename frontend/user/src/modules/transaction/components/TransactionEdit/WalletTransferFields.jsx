import React from 'react';
import { Form } from 'antd';
import WalletSelect from 'src/features/forms/WalletSelect';
import FormQuantityInput from 'src/features/forms/FormQuantityInput';

const WalletTransferFields = ({
  getWallets,
  fromWallet,
  baseTicker,
  isCounterTransaction,
  onAddWallet,
}) => {

  const form = Form.useFormInstance();
  const wallet2IdValue = Form.useWatch('wallet2Id', form);
  const quantityValue = Form.useWatch('quantity', form);
  const wallets = getWallets({ excludeId: fromWallet?.id, showTickerId: baseTicker?.id });

  return (
    <>

    {/* Кошелек отправитель */}
    <Form.Item name="walletId" hidden initialValue={fromWallet?.id}>
      <input />
    </Form.Item>

    {/* Кошелек получатель */}
    <WalletSelect
      name='wallet2Id'
      label='Кошелек получатель'
      rules={[{ required: true, message: 'Выберите кошелек' }]}
      hidden={isCounterTransaction}
      variant="filled"
      status={!wallet2IdValue ? 'warning' : undefined}
      placeholder="Выберите кошелек получатель"
      options={wallets}
      onAddWallet={onAddWallet}
      fieldNames={{label: 'name', value: 'id'}}
      optionRender={(o) => (<>
        {o.data.name}
        <span className='option-subtext'>({o.data.free} {baseTicker?.symbol})</span>
      </>)}
    />

    {/* Количество */}
    <FormQuantityInput
      showFree={true}
      walletFree={fromWallet?.baseAssetFree}
      ticker={baseTicker?.symbol}
      status={wallet2IdValue && !quantityValue ? 'warning' : undefined}
    />
    </>
  );
};

export default WalletTransferFields;
