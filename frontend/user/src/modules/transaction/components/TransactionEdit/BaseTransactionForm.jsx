import React from 'react';
import { Form } from 'antd';
import { PORTFOLIO_TYPES, WALLET_TYPES } from 'src/modules/transaction/constants/transactionTypes';
import { useTransactionForm } from './hooks/useTransactionForm';
import { useTransactionData } from './hooks/useTransactionData';
import FormComment from 'src/features/forms/FormComment';
import FormDate from 'src/features/forms/FormDate';
import FormRadioGroup from 'src/features/forms/FormRadioGroup';
import FormActionBtns from 'src/features/forms/FormActionBtns';
import PortfolioTradeFields from './PortfolioTradeFields';
import PortfolioTransferFields from './PortfolioTransferFields';
import PortfolioInOutFields from './PortfolioInOutFields';
import WalletTransferFields from './WalletTransferFields';
import ShowMore from 'src/components/ui/ShowMore';
import { getTransactionTypeInfo } from 'src/modules/transaction/utils/type';

const BaseTransactionForm = ({ tickerId, portfolioId, walletId, transaction, onCancel, onSubmit, loading }) => {

  const availableTypes = portfolioId ? PORTFOLIO_TYPES : WALLET_TYPES;

  const {
    form,
    transactionType, handleTypeChange,
    calculationType, toggleCalculationType,
  } = useTransactionForm(transaction, availableTypes[0].value);

  const { isTrade, isTransfer, isInOut, isEarning } = getTransactionTypeInfo(transactionType);

  const {
    transactionPortfolio,
    wallets, handleWalletChange, transactionWallet,
    handleQuoteTickerChange, baseTicker, quoteTicker,
    isCounterTransaction,
    getPortfolios,
    getWallets,
  } = useTransactionData({ tickerId, portfolioId, walletId, transaction, transactionType, form });

  const handleSubmit = async (values) => {
    const submitData = {
      ...values,
      ...(transaction && { id: transaction.id }), // Добавляем ID если редактируем
      ...(isTrade && { priceUsd: form.getFieldValue('price') * quoteTicker?.price }),
      tickerId: baseTicker?.id,
    };
    onSubmit(submitData);
  };

  const handleCancel = () => {
    form.resetFields();
    onCancel();
  };

  const getFormFields = () => {
    if (portfolioId) {
      if (isTrade) return (
        <PortfolioTradeFields 
          transaction={transaction}
          wallet={transactionWallet}
          handleWalletChange={handleWalletChange}
          getWallets={getWallets}
          baseTicker={baseTicker}
          portfolio={transactionPortfolio}
          calculationType={calculationType}
          toggleCalculationType={toggleCalculationType}
          quoteTicker={quoteTicker}
          handleQuoteTickerChange={handleQuoteTickerChange}
          transactionType={transactionType}
        />
      );
      if (isTransfer) return (
        <PortfolioTransferFields 
          getPortfolios={getPortfolios}
          fromPortfolio={transactionPortfolio}
          baseTicker={baseTicker}
          isCounterTransaction={isCounterTransaction}
        />
      );
      if (isInOut || isEarning) return (
        <PortfolioInOutFields 
          getWallets={getWallets}
          wallet={transactionWallet}
          portfolio={transactionPortfolio}
          baseTicker={baseTicker}
          transactionType={transactionType}
          handleWalletChange={handleWalletChange}
        />
      );
    } else if (walletId) {
      if (isTransfer) return (
        <WalletTransferFields 
          getWallets={getWallets}
          fromWallet={transactionWallet}
          baseTicker={baseTicker}
          isCounterTransaction={isCounterTransaction}
        />
      );
    }
  };

  return (
    <Form
      form={form}
      onFinish={handleSubmit}
      // requiredMark="optional"
      requiredMark={false}
      size="middle"
    >
      {/* Тип транзакции */}
      <FormRadioGroup name='type' btns={availableTypes} onChange={handleTypeChange}/>

      {/* Специфические поля */}
      {getFormFields()}

      {/* Дата */}
      <FormDate />

      {/* Кнопка "Еще" */}
      <ShowMore content={<FormComment />} show={transaction?.comment}/>

      {/* Кнопки действий */}
      <FormActionBtns
        title={transaction ? 'Сохранить' : 'Добавить'} 
        onCancel={handleCancel}
        loading={loading}
      />
    </Form>
  );
};

export default BaseTransactionForm;
