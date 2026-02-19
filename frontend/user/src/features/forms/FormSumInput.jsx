import { Form, Button, InputNumber } from 'antd';

const exists = (value) => value !== undefined && value !== null && value !== false;

const FormSumInput = ({ showFree, walletFree, ticker, onChange, disabled }) => {
  const form = Form.useFormInstance();

  const freeAmount = (() => {
    if (!showFree) return undefined;

    if (exists(walletFree)) {
      return walletFree;
    }
    return 0;
  })();

  const handlePasteMax = () => {
    form.setFieldValue('quantity2', freeAmount);
    if (onChange) onChange();
  };

  // Правила валидации
  const rules = [{ required: true, message: 'Введите сумму' }];

  // Добавляем правило максимального значения только если freeAmount определен
  if (exists(freeAmount)) {
    rules.push({ max: freeAmount, message: 'Превышает доступную сумму в кошельке', type: 'number' });
  }

  return (
    <Form.Item
      extra={
        <div style={{ fontSize: '12px', display: 'flex' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {/* Информация о доступном количестве */}
            {showFree && exists(walletFree) && (
              <div style={{ fontSize: '12px', color: walletFree > 0 ? 'inherit' : 'red' }}>
                В кошельке: {walletFree} {ticker}
              </div>
            )}
          </div>
          {showFree && freeAmount > 0 && (
            <Button type="link" onClick={handlePasteMax} style={{ padding: 0, marginLeft: 'auto' }}>MAX</Button>
          )}
        </div>
      }
      label={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          Сумма транзакции
        </div>
      }
      name="quantity2"
      rules={rules}
    >
      <InputNumber
        addonBefore={ticker || '—'}
        placeholder="0.00"
        // step="0.01"
        // min="0.01"
        max={freeAmount}
        // precision={2}
        style={{ width: '100%' }}
        disabled={disabled}
        onChange={onChange}
      />
    </Form.Item>
  );
};

export default FormSumInput;
