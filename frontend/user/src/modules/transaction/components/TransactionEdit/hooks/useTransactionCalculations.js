import { useCallback, useEffect, useRef } from 'react';
import { Form } from 'antd';

const exists = (value) => value !== undefined && value !== null && value !== '';

export const useTransactionCalculations = (form) => {
  const price = Form.useWatch('price', form);

  // Поле, которое пользователь редактировал последним — оно считается исходным
  const lastEditedRef = useRef('amount');

  const handleQuantityChange = useCallback(() => {
    lastEditedRef.current = 'quantity';
    const quantity = form.getFieldValue('quantity');
    const price = form.getFieldValue('price');
    const amount = (parseFloat(quantity) || 0) * (parseFloat(price) || 0);
    form.setFieldValue('quantity2', amount);
  }, [form]);

  const handleAmountChange = useCallback(() => {
    lastEditedRef.current = 'amount';
    const amount = form.getFieldValue('quantity2');
    const price = form.getFieldValue('price');
    const quantity = (parseFloat(amount) || 0) / (parseFloat(price) || 1);
    form.setFieldValue('quantity', quantity);
  }, [form]);

  const handlePriceChange = useCallback(() => {
    const price = form.getFieldValue('price');
    if (lastEditedRef.current === 'amount') {
      // Исходная сумма — пересчитываем количество
      const amount = form.getFieldValue('quantity2');
      if (exists(amount)) {
        form.setFieldValue('quantity', (parseFloat(amount) || 0) / (parseFloat(price) || 1));
      }
    } else {
      // Исходное количество — пересчитываем сумму
      const quantity = form.getFieldValue('quantity');
      if (exists(quantity)) {
        form.setFieldValue('quantity2', (parseFloat(quantity) || 0) * (parseFloat(price) || 0));
      }
    }
  }, [form]);

  // Пересчитываем производное поле при изменении цены (в т.ч. программном — при выборе валюты цены)
  useEffect(() => {
    const priceValue = parseFloat(price) || 0;
    if (!priceValue) return;

    if (lastEditedRef.current === 'quantity') {
      const quantity = form.getFieldValue('quantity');
      if (exists(quantity)) {
        form.setFieldValue('quantity2', (parseFloat(quantity) || 0) * priceValue);
      }
    } else {
      const amount = form.getFieldValue('quantity2');
      if (exists(amount)) {
        form.setFieldValue('quantity', (parseFloat(amount) || 0) / priceValue);
      }
    }
  }, [price, form]);

  return {
    handleQuantityChange,
    handleAmountChange,
    handlePriceChange,
  };
};
