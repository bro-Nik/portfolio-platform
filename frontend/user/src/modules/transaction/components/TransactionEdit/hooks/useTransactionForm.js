import { useState, useEffect } from 'react';
import { Form } from 'antd';
import dayjs from 'dayjs';

export const useTransactionForm = (transaction, type) => {
  const [form] = Form.useForm();
  const [transactionType, setTransactionType] = useState(transaction?.type || type);

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
    setTransactionType(type);
  };

  return {
    form,
    transactionType,
    handleTypeChange,
  };
};
