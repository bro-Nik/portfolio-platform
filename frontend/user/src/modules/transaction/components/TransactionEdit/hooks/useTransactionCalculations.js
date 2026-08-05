import { useCallback, useEffect } from 'react';
import { Form } from 'antd';

const exists = (value) => value !== undefined && value !== null && value !== '';

export const useTransactionCalculations = (form, calculationType) => {
  const price = Form.useWatch('price', form);

  const handleQuantityChange = useCallback(() => {
    const quantity = form.getFieldValue('quantity');
    const price = form.getFieldValue('price');
    const amount = (parseFloat(quantity) || 0) * (parseFloat(price) || 0);
    form.setFieldValue('quantity2', amount);
  }, [form]);

  const handleAmountChange = useCallback(() => {
    const amount = form.getFieldValue('quantity2');
    const price = form.getFieldValue('price');
    const quantity = (parseFloat(amount) || 0) / (parseFloat(price) || 1);
    form.setFieldValue('quantity', quantity);
  }, [form]);

  const handlePriceChange = useCallback(() => {
    const price = form.getFieldValue('price');
    let quantity = form.getFieldValue('quantity');
    let amount = form.getFieldValue('quantity2');

    if (exists(quantity) && (!exists(amount) || calculationType === 'amount')) {
      // Если не заполнена сумма или включен режим количество
      amount = (parseFloat(quantity) || 0) * (parseFloat(price) || 0);
      form.setFieldValue('quantity2', amount);
    } else if (exists(amount) && (!exists(quantity) || calculationType === 'quantity')) {
      // Если не заполнено количество или включен режим сумма
      quantity = (parseFloat(amount) || 0) / (parseFloat(price) || 1);
      form.setFieldValue('quantity', quantity);
    }
  }, [form, calculationType]);

  // Пересчитываем производное поле при изменении цены (в т.ч. программном — при выборе валюты цены)
  useEffect(() => {
    const priceValue = parseFloat(price) || 0;
    if (!priceValue) return;

    if (calculationType === 'quantity') {
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
  }, [price, calculationType, form]);

  return {
    handleQuantityChange,
    handleAmountChange,
    handlePriceChange,
  };
};
