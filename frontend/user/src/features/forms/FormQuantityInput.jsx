import { Form, Button, InputNumber, Space } from 'antd';

const exists = (value) => value !== undefined && value !== null && value !== false;

const FormQuantityInput = ({ showFree, walletFree, portfolioFree, ticker, onChange, disabled, status }) => {
  const form = Form.useFormInstance();
  const quantityValue = Form.useWatch('quantity', form);

  const freeAmount = (() => {
    if (!showFree) return undefined;

    const walletFreeNum = exists(walletFree) ? Number(walletFree) : undefined;
    const portfolioFreeNum = exists(portfolioFree) ? Number(portfolioFree) : undefined;

    if (exists(walletFreeNum) && exists(portfolioFreeNum)) {
      return Math.min(walletFreeNum, portfolioFreeNum);
    }
    else if (exists(walletFreeNum)) {
      return walletFreeNum;
    }
    else if (exists(portfolioFreeNum)) {
      return portfolioFreeNum;
    }
    return 0;
  })();

  const handlePasteMax = () => {
    form.setFieldValue('quantity', freeAmount);
    form.validateFields(['quantity']);
    if (onChange) onChange();
  };

  const handleRawInput = (raw) => {
    const num = Number(raw);
    if (exists(freeAmount) && raw !== '' && !Number.isNaN(num) && num > freeAmount) {
      form.setFields([{ name: 'quantity', errors: ['Больше, чем доступно'] }]);
    }
  };

  // Правила валидации
  const rules = [{ required: true, message: 'Введите количество' }];

  // Добавляем правило максимального значения только если freeAmount определен и больше нуля
  if (exists(freeAmount) && freeAmount > 0) {
    rules.push({ max: freeAmount, message: 'Больше, чем доступно', type: 'number' });
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
            {showFree && exists(portfolioFree) && (
              <div style={{ fontSize: '12px', color: portfolioFree > 0 ? 'inherit' : 'red' }}>
                В портфеле: {portfolioFree} {ticker}
              </div>
            )}
          </div>
        </div>
      }
      label={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <span>Количество</span>
        </div>
      }
    >
        <Form.Item
          style={{ width: '100%', marginBottom: 0 }}
          name="quantity"
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
                <span>{ticker || '—'}</span>
                {showFree && freeAmount > 0 && quantityValue !== freeAmount && (
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

export default FormQuantityInput;
