import { Form, Button, InputNumber, Space } from 'antd';

const exists = (value) => value !== undefined && value !== null && value !== false;

const FormSumInput = ({ showFree, walletFree, ticker, onChange, disabled, status }) => {
  const form = Form.useFormInstance();

  const freeAmount = (() => {
    if (!showFree) return undefined;

    if (exists(walletFree)) {
      return Number(walletFree);
    }
    return 0;
  })();

  const handlePasteMax = () => {
    form.setFieldValue('quantity2', freeAmount);
    form.validateFields(['quantity2']);
    if (onChange) onChange();
  };

  const handleRawInput = (raw) => {
    const num = Number(raw);
    if (exists(freeAmount) && raw !== '' && !Number.isNaN(num) && num > freeAmount) {
      form.setFields([{ name: 'quantity2', errors: ['Превышает доступную сумму в кошельке'] }]);
    }
  };

  // Правила валидации
  const rules = [{ required: true, message: 'Введите сумму' }];

  // Добавляем правило максимального значения только если freeAmount определен и больше нуля
  if (exists(freeAmount) && freeAmount > 0) {
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
        </div>
      }
      label={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          Сумма транзакции
        </div>
      }
    >
        <Form.Item
          style={{ width: '100%', marginBottom: 0 }}
          name="quantity2"
          rules={rules}
        >
          <InputNumber
            placeholder="0.00"
            max={freeAmount}
            style={{ width: '100%' }}
            disabled={disabled}
            status={status}
            onInput={handleRawInput}
            onChange={onChange}
            variant="filled"
            suffix={
              <Space size={4}>
                <span>{ticker}</span>
                {showFree && freeAmount > 0 && (
                  <Button
                    type="link"
                    size="small"
                    onClick={handlePasteMax}
                    onMouseDown={(e) => e.stopPropagation()}
                    style={{ padding: 0, height: 'auto', pointerEvents: 'auto' }}
                  >MAX</Button>
                )}
              </Space>
            }
          />
        </Form.Item>
    </Form.Item>
  );
};

export default FormSumInput;
