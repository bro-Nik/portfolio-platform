import React from 'react';
import { Form, InputNumber, Space, Segmented, Button } from 'antd';
import { useTransactionCalculations } from './hooks/useTransactionCalculations';
import FormCheckbox from 'src/features/forms/FormCheckbox';
import FormSelect from 'src/features/forms/FormSelect';
import WalletSelect from 'src/features/forms/WalletSelect';
import FormQuantityInput from 'src/features/forms/FormQuantityInput';
import FormSumInput from 'src/features/forms/FormSumInput';
import { getTransactionTypeInfo } from 'src/modules/transaction/utils/type';

const PortfolioTradeFields = ({
  transaction,
  getWallets,
  wallet,
  portfolio,
  handleWalletChange,
  baseTicker,
  quoteTicker,
  calculationType,
  setCalculationType,
  handleQuoteTickerChange,
  transactionType,
  onAddWallet,
  onFundWallet,
}) => {

  const form = Form.useFormInstance();
  const { handleQuantityChange, handleAmountChange, handlePriceChange } = useTransactionCalculations(form, calculationType);
  const { isSell } = getTransactionTypeInfo(transactionType);
  const walletIdValue = Form.useWatch('walletId', { form, preserve: true });
  const ticker2IdValue = Form.useWatch('ticker2Id', form);
  const quantityValue = Form.useWatch('quantity', form);
  const amountValue = Form.useWatch('quantity2', form);

  const nextStepDone = wallet && quoteTicker;

  const walletsToBuy = getWallets({});
  const walletsToSell = getWallets({ showTickerId: baseTicker?.id });

  return (
    <>

    {/* Портфель */}
    <Form.Item name="portfolioId" hidden initialValue={portfolio?.id}>
      <input />
    </Form.Item>

    {/* Ордер */}
    <FormCheckbox name="order" label="Ордер" checked={transaction?.order} />

    {/* Кошелек */}
    <WalletSelect
      name="walletId"
      label={(
        <div style={{ display: 'flex', alignItems: 'center' }}>
          Кошелек
          {walletIdValue && (
            <Button
              type="link"
              size="small"
              style={{ padding: 0, height: 'auto', marginLeft: 12 }}
              onClick={onFundWallet}
            >
              Пополнить
            </Button>
          )}
        </div>
      )}
      rules={[{ required: true, message: 'Выберите кошелек' }]}
      onChange={handleWalletChange}
      variant="filled"
      status={!wallet ? 'warning' : undefined}
      placeholder="Выберите кошелек"
      fieldNames={{label: 'name', value: 'id'}}
      options={isSell ? walletsToSell : walletsToBuy}
      onAddWallet={onAddWallet}
      optionRender={(o) => (<>
        {o.data.name}
        {o.data.free !== undefined ? <span className='option-subtext'>({o.data.free} {baseTicker?.symbol})</span> : null}
      </>)}
    />

    {/* Цена */}
    <Form.Item label="Цена">
      <Space.Compact style={{ width: '100%' }}>
        <FormSelect
          name="ticker2Id"
          noStyle
          variant="filled"
          style={{ width: 'auto', flex: '0 0 auto', minWidth: 110, maxWidth: '60%' }}
          rules={[{ required: true, message: 'Выберите валюту' }]}
          showSearch
          popupMatchSelectWidth={false}
          placeholder={!wallet ? undefined : !wallet?.assets?.length ? 'В кошельке нет активов' : 'Выберите актив'}
          onChange={handleQuoteTickerChange}
          disabled={!wallet || !wallet?.assets?.length}
          status={wallet?.assets?.length && !ticker2IdValue ? 'warning' : undefined}
          fieldNames={{label: 'symbol', value: 'tickerId'}}
          options={wallet?.assets}
          optionRender={(o) => (<>
            {o.data.symbol}
            {o.data.free !== undefined ? <span className='option-subtext'>({o.data.free} {o.data.symbol})</span> : null}
          </>)}
        />
        <Form.Item
          name="price"
          noStyle
          rules={[{ required: true, message: 'Введите цену' }]}
          initialValue={transaction?.priceUsd}
        >
          <InputNumber
            placeholder="0.00"
            onChange={handlePriceChange}
            step="0.01"
            min="0"
            style={{ width: '100%' }}
            disabled={!wallet || !wallet?.assets?.length}
            variant="filled"
          />
        </Form.Item>
      </Space.Compact>
    </Form.Item>

    {/* Выбор активного поля транзакции (Сумма, Количество) */}
    <Form.Item>
      <Segmented
        value={calculationType}
        options={[{ label: 'Сумма', value: 'amount' }, { label: 'Количество', value: 'quantity' }]}
        onChange={setCalculationType}
      />
    </Form.Item>

    {/* Количество */}
    <FormQuantityInput
      showFree={isSell}
      walletFree={wallet?.baseAssetFree}
      portfolioFree={portfolio?.baseAssetFree}
      ticker={baseTicker?.symbol}
      onChange={handleQuantityChange}
      disabled={calculationType !== 'quantity'}
      status={calculationType === 'quantity' && nextStepDone && !quantityValue ? 'warning' : undefined}
    />

    {/* Сумма транзакции */}
    <FormSumInput
      showFree={!isSell}
      walletFree={quoteTicker ? wallet?.quoteAssetFree : undefined}
      ticker={quoteTicker?.symbol}
      onChange={handleAmountChange}
      disabled={calculationType !== 'amount' || !quoteTicker}
      status={calculationType === 'amount' && nextStepDone && !amountValue ? 'warning' : undefined}
    />
    </>
  );
};

export default PortfolioTradeFields;
