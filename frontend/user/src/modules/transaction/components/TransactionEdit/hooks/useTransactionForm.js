import { useState, useCallback, useEffect } from 'react';
import { Form } from 'antd';
import { toDatetimeLocal } from 'src/utils/format';

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
      date: toDatetimeLocal(transaction?.date || new Date()),
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
