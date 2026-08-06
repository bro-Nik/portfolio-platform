import React, { useRef } from 'react';
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
import WalletForm from 'src/modules/wallets/components/WalletForm';
import PortfolioForm from 'src/modules/portfolios/components/PortfolioForm';
import WalletFundingForm from 'src/modules/wallets/components/WalletFundingForm';
import SubviewHeader from 'src/components/ui/SubviewHeader';
import { getTransactionTypeInfo } from 'src/modules/transaction/utils/type';
import { toUsd } from 'src/utils/currency';

const BaseTransactionForm = ({ tickerId, portfolioId, walletId, transaction, onCancel, onSubmit, loading, subview, openSubview, closeSubview }) => {

  const availableTypes = portfolioId ? PORTFOLIO_TYPES : WALLET_TYPES;

  const {
    form,
    transactionType, handleTypeChange,
    calculationType, setCalculationType,
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
      ...(transactionType === 'Input' && {
        priceUsd: form.getFieldValue('inputPrice') == null
          ? null
          : toUsd(form.getFieldValue('inputPrice')),
      }),
      tickerId: baseTicker?.id,
    };
    onSubmit(submitData);
  };

  const handleCancel = () => {
    form.resetFields();
    onCancel();
  };

  const walletTargetRef = useRef('walletId');

  const openWalletSubview = (field = 'walletId') => {
    walletTargetRef.current = field;
    openSubview('wallet');
  };

  const handleWalletCreated = (wallet) => {
    const field = walletTargetRef.current;
    form.setFieldValue(field, wallet.id);
    if (field === 'walletId') {
      handleWalletChange(wallet);
    }
    closeSubview();
  };

  const portfolioTargetRef = useRef('portfolio2Id');

  const openPortfolioSubview = (field = 'portfolio2Id') => {
    portfolioTargetRef.current = field;
    openSubview('portfolio');
  };

  const handlePortfolioCreated = (portfolio) => {
    form.setFieldValue(portfolioTargetRef.current, portfolio.id);
    closeSubview();
  };

  const walletIdValue = Form.useWatch('walletId', { form, preserve: true });

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
          setCalculationType={setCalculationType}
          quoteTicker={quoteTicker}
          handleQuoteTickerChange={handleQuoteTickerChange}
          transactionType={transactionType}
          onAddWallet={() => openWalletSubview('walletId')}
          onFundWallet={() => openSubview('funding')}
        />
      );
      if (isTransfer) return (
        <PortfolioTransferFields 
          getPortfolios={getPortfolios}
          fromPortfolio={transactionPortfolio}
          baseTicker={baseTicker}
          isCounterTransaction={isCounterTransaction}
          onCreatePortfolio={() => openPortfolioSubview('portfolio2Id')}
        />
      );
      if (isInOut || isEarning) return (
        <PortfolioInOutFields 
          getWallets={getWallets}
          wallet={transactionWallet}
          portfolio={transactionPortfolio}
          baseTicker={baseTicker}
          transaction={transaction}
          transactionType={transactionType}
          handleWalletChange={handleWalletChange}
          onAddWallet={() => openWalletSubview('walletId')}
        />
      );
    } else if (walletId) {
      if (isTransfer) return (
        <WalletTransferFields 
          getWallets={getWallets}
          fromWallet={transactionWallet}
          baseTicker={baseTicker}
          isCounterTransaction={isCounterTransaction}
          onAddWallet={() => openWalletSubview('wallet2Id')}
        />
      );
    }
  };
  const date = Form.useWatch('date', { form, preserve: true });

  if (subview === 'wallet') {
    return (
      <>
        <SubviewHeader title="Добавить кошелек" onBack={closeSubview} />
        <WalletForm
          wallet={null}
          submitText="Создать"
          onSuccess={handleWalletCreated}
          onCancel={closeSubview}
        />
      </>
    );
  }

  if (subview === 'portfolio') {
    return (
      <>
        <SubviewHeader title="Добавить портфель" onBack={closeSubview} />
        <PortfolioForm
          initialMarket={transactionPortfolio?.market}
          submitText="Создать"
          onSuccess={handlePortfolioCreated}
          onCancel={closeSubview}
        />
      </>
    );
  }

  if (subview === 'funding') {
    return (
      <>
        <SubviewHeader title="Пополнение" onBack={closeSubview} />
        <WalletFundingForm
          walletId={walletIdValue}
          portfolioId={transactionPortfolio?.id}
          onSuccess={closeSubview}
          onCancel={closeSubview}
        />
      </>
    );
  }

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
