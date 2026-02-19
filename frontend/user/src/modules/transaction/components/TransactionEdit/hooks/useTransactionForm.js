import { useState, useCallback, useEffect } from 'react';
import { Form } from 'antd';

export const useTransactionForm = (transaction, type) => {
  const [form] = Form.useForm();
  const [transactionType, setTransactionType] = useState(transaction?.type || type);
  const [calculationType, setCalculationType] = useState('amount');

  const toggleCalculationType = useCallback(() => setCalculationType(prev => prev === 'amount' ? 'quantity' : 'amount'), []);

  useEffect(() => {
    const initialValues = {
      ...(transaction && { ...transaction }),
      type: transaction?.type || type,
      order: transaction?.order || false,
      date: transaction?.date ? new Date(transaction.date).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16),
    };

    form.setFieldsValue(initialValues);
  }, [transaction, form, type]);

  const handleTypeChange = (type) => {
    // const type = e.target.value;
    setTransactionType(type);
  };

  return {
    form,
    transactionType,
    handleTypeChange,
    calculationType,
    toggleCalculationType,
  };
};
