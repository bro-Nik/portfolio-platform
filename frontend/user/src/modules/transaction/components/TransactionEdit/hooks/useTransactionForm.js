import { useState, useCallback, useEffect } from 'react';
import { Form } from 'antd';
import dayjs from 'dayjs';

export const useTransactionForm = (transaction, type) => {
  const [form] = Form.useForm();
  const [transactionType, setTransactionType] = useState(transaction?.type || type);
  const [calculationType, setCalculationTypeState] = useState('amount');

  const setCalculationType = useCallback((value) => setCalculationTypeState(value), []);

  useEffect(() => {
    const initialValues = {
      ...(transaction && { ...transaction }),
      type: transaction?.type || type,
      order: transaction?.order || false,
      date: transaction?.date ? dayjs(transaction.date) : dayjs(),
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
    setCalculationType,
  };
};
