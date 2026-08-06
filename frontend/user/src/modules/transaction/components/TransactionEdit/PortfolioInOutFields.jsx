import React, { useEffect } from 'react';
import { Button, Form, InputNumber, Space } from 'antd';
import WalletSelect from 'src/features/forms/WalletSelect';
import FormQuantityInput from 'src/features/forms/FormQuantityInput';
import { getTransactionTypeInfo } from 'src/modules/transaction/utils/type';
import { DISPLAY_CURRENCY, fromUsd } from 'src/utils/currency';

const PortfolioInOutFields = ({
  getWallets,
  baseTicker,
  portfolio,
  wallet,
  transaction,
  transactionType,
  handleWalletChange,
  onAddWallet,
}) => {

  const { isSpend } = getTransactionTypeInfo(transactionType);
  const form = Form.useFormInstance();
  const quantityValue = Form.useWatch('quantity', form);
  const wallets = getWallets({ showTickerId: baseTicker?.id });
  const isInput = transactionType === 'Input';
  const inputPriceValue = Form.useWatch('inputPrice', form);
  const marketPrice = baseTicker?.price ? fromUsd(baseTicker.price) : null;

  useEffect(() => {
    if (!isInput) return;
    const current = form.getFieldValue('inputPrice');
    if (current != null && current !== '') return;
    const existing = transaction?.priceUsd;
    if (existing != null) {
      form.setFieldValue('inputPrice', fromUsd(existing));
    } else if (baseTicker?.price) {
      form.setFieldValue('inputPrice', fromUsd(baseTicker.price));
    }
  }, [isInput, transaction?.priceUsd, baseTicker?.price, form]);

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

    {/* Цена (только для Input — база amount) */}
    {isInput && (
      <Form.Item label="Цена">
        <Form.Item
          name="inputPrice"
          noStyle
        >
          <InputNumber
            placeholder="0.00"
            step="0.01"
            min="0"
            style={{ width: '100%' }}
            variant="filled"
            suffix={(
              <Space size={4}>
                <span>{DISPLAY_CURRENCY}</span>
                {inputPriceValue !== marketPrice && marketPrice != null ? (
                  <Button
                    type="link"
                    size="small"
                    onClick={() => {
                      form.setFieldValue('inputPrice', marketPrice);
                      form.validateFields(['inputPrice']);
                    }}
                    onMouseDown={(e) => e.stopPropagation()}
                    style={{ padding: 0, height: 'auto', pointerEvents: 'auto' }}
                  >Рыночная</Button>
                ) : null}
              </Space>
            )}
          />
        </Form.Item>
      </Form.Item>
    )}
    </>
  );
};

export default PortfolioInOutFields;
