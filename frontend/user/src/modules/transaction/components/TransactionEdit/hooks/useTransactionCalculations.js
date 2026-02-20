import { useCallback } from 'react';

const exists = (value) => value !== undefined && value !== null && value !== '';

export const useTransactionCalculations = (form, calculationType) => {
  const handleQuantityChange = useCallback(() => {
    const quantity = form.getFieldValue('quantity');
    const price = form.getFieldValue('price');
    if (price) {
      const amount = (parseFloat(quantity) || 0) * (parseFloat(price) || 0);
      form.setFieldValue('quantity2', amount);
    }
  }, [form]);

  const handleAmountChange = useCallback(() => {
    const amount = form.getFieldValue('quantity2');
    const price = form.getFieldValue('price');
    if (price) {
      const quantity = (parseFloat(amount) || 0) / (parseFloat(price) || 1);
      form.setFieldValue('quantity', quantity);
    }
  }, [form]);

  const handlePriceChange = useCallback(() => {
    const price = form.getFieldValue('price');
    let quantity = form.getFieldValue('quantity');
    let amount = form.getFieldValue('quantity2');

    
    if (exists(quantity) && (!exists(amount) || calculationType === 'amount')) {
      // Если не заполненна сумма или включен режим количество
      amount = (parseFloat(quantity) || 0) * (parseFloat(price) || 0);
      form.setFieldValue('quantity2', amount);
    } else if (exists(amount) && (!exists(quantity) || calculationType === 'quantity')) {
      // Если не заполненно количество или включен режим сумма
      quantity = (parseFloat(amount) || 0) / (parseFloat(price) || 1);
      form.setFieldValue('quantity', quantity);
    }
  }, [form, calculationType]);

  return {
    handleQuantityChange,
    handleAmountChange,
    handlePriceChange,
  };
};
