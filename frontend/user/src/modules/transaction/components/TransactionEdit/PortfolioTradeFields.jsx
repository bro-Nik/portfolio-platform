import React from 'react';
import { Form, Button, InputNumber, Space, Segmented } from 'antd';
import { useTransactionCalculations } from './hooks/useTransactionCalculations';
import FormCheckbox from '/app/src/features/forms/FormCheckbox';
import FormSelect from '/app/src/features/forms/FormSelect';
import FormQuantityInput from '/app/src/features/forms/FormQuantityInput';
import FormSumInput from '/app/src/features/forms/FormSumInput';
import { getTransactionTypeInfo } from '/app/src/modules/transaction/utils/type';

const PortfolioTradeFields = ({
  transaction,
  getWallets,
  wallet,
  portfolio,
  handleWalletChange,
  baseTicker,
  quoteTicker,
  calculationType,
  toggleCalculationType,
  handleQuoteTickerChange,
  transactionType,
}) => {

  const form = Form.useFormInstance();
  const { handleQuantityChange, handleAmountChange, handlePriceChange } = useTransactionCalculations(form, calculationType);
  const { isSell } = getTransactionTypeInfo(transactionType);

  const walletsToBuy = getWallets({});
  const walletsToSell = getWallets({ showTickerId: baseTicker?.id });

  return (
    <>
    {/* Портфель */}
    <Form.Item name="portfolioId" hidden initialValue={portfolio?.id}></Form.Item>

    {/* Ордер */}
    <FormCheckbox name="order" label="Ордер" checked={transaction?.order} />

    {/* Кошелек */}
    <FormSelect
      name="walletId"
      label='Кошелек' 
      rules={[{ required: true, message: 'Выберите кошелек' }]}
      onChange={handleWalletChange}
      fieldNames={{label: 'name', value: 'id'}}
      options={isSell ? walletsToSell : walletsToBuy}
      optionRender={(o, { index }) => (<>
        {o.data.name}
        {o.data.free !== undefined ? <span className='option-subtext'>({o.data.free} {baseTicker?.symbol})</span> : null}
      </>)}
    />

    {/* Цена */}
    <Form.Item label="Цена">
      <Space.Compact>
        <FormSelect
          name="ticker2Id"
          noStyle
          rules={[{ required: true, message: 'Выберите валюту' }]}
          showSearch
          popupMatchSelectWidth={false}
          placeholder="Валюта"
          onChange={handleQuoteTickerChange}
          disabled={!wallet?.assets?.length}
          fieldNames={{label: 'symbol', value: 'tickerId'}}
          options={wallet?.assets}
          optionRender={(o, { index }) => (<>
            {o.data.symbol}
            {o.data.free !== undefined ? <span className='option-subtext'>({o.data.free} {o.data.symbol})</span> : null}
          </>)}
        />
        <Form.Item 
          name="price"
          noStyle
          rules={[{ required: true, message: 'Введите цену' }]}
        >
          <InputNumber
            placeholder="0.00"
            onChange={handlePriceChange}
            step="0.01"
            min="0"
            defaultValue={transaction?.priceUsd}
            disabled={!wallet}
          />
        </Form.Item>
      </Space.Compact>
    </Form.Item>

    {/* Количество */}
    <FormQuantityInput
      showFree={isSell}
      walletFree={wallet?.baseAssetFree}
      portfolioFree={portfolio?.baseAssetFree}
      ticker={baseTicker?.symbol}
      onChange={handleQuantityChange}
      disabled={calculationType !== 'quantity'}
    />

    {/* Выбор активного поля транзакции (Сумма, Количество) */}
    <Form.Item>
      <Segmented size="small" options={['Сумма', 'Количество']} onChange={toggleCalculationType} />
    </Form.Item>

    {/* Сумма транзакции */}
    <FormSumInput
      showFree={!isSell}
      walletFree={wallet?.quoteAssetFree}
      ticker={quoteTicker?.symbol}
      onChange={handleAmountChange}
      disabled={calculationType !== 'amount'}
    />
    </>
  );
};

export default PortfolioTradeFields;
