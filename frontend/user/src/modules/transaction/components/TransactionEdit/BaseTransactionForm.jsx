import React from 'react';
import { Form } from 'antd';
import { PORTFOLIO_TYPES, WALLET_TYPES } from 'src/modules/transaction/constants/transactionTypes';
import { useTransactionForm } from './hooks/useTransactionForm';
import { useTransactionData } from './hooks/useTransactionData';
import FormRadioGroup from 'src/features/forms/FormRadioGroup';
import FormActionBtns from 'src/features/forms/FormActionBtns';
import PortfolioTradeFields from './PortfolioTradeFields';
import PortfolioTransferFields from './PortfolioTransferFields';
import PortfolioInOutFields from './PortfolioInOutFields';
import WalletTransferFields from './WalletTransferFields';
import MetaRowGroup from 'src/components/ui/MetaRowGroup';
import DateSubview from 'src/features/forms/DateSubview';
import CommentSubview from 'src/features/forms/CommentSubview';
import { getTransactionTypeInfo } from 'src/modules/transaction/utils/type';

const BaseTransactionForm = ({ tickerId, portfolioId, walletId, transaction, onCancel, onSubmit, loading, subview, openSubview, closeSubview }) => {

  const availableTypes = portfolioId ? PORTFOLIO_TYPES : WALLET_TYPES;

  const {
    form,
    transactionType, handleTypeChange,
    calculationType, toggleCalculationType,
  } = useTransactionForm(transaction, availableTypes[0].value);

  const { isTrade, isTransfer, isInOut, isEarning } = getTransactionTypeInfo(transactionType);

  const {
    transactionPortfolio,
    handleWalletChange, transactionWallet,
    handleQuoteTickerChange, baseTicker, quoteTicker,
    isCounterTransaction,
    getPortfolios,
    getWallets,
  } = useTransactionData({ tickerId, portfolioId, walletId, transaction, transactionType, form });

  const handleSubmit = async (values) => {
    const submitData = {
      ...values,
      ...(values.date && { date: values.date.toISOString?.() || new Date(values.date).toISOString() }),
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
  const date = Form.useWatch('date', { form, preserve: true });

  return (
    <Form
      form={form}
      onFinish={handleSubmit}
      layout="vertical"
      requiredMark={false}
      size="middle"
    >
      {subview === 'date' ? (
        <DateSubview onClose={closeSubview} />
      ) : subview === 'comment' ? (
        <CommentSubview onClose={closeSubview} />
      ) : (
        <>
          {/* Тип транзакции */}
          <FormRadioGroup name='type' btns={availableTypes} onChange={handleTypeChange}/>

          {/* Специфические поля */}
          {getFormFields()}

          {/* Дата / Комментарий */}
          <MetaRowGroup
            date={date}
            onDate={() => openSubview('date')}
            onComment={() => openSubview('comment')}
          />

          {/* Кнопки действий */}
          <FormActionBtns title="Сохранить" onCancel={handleCancel} loading={loading} />
        </>
      )}
    </Form>
  );
};

export default BaseTransactionForm;
