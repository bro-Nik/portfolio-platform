import { Form, Button, InputNumber } from 'antd';

const exists = (value) => value !== undefined && value !== null && value !== false;

const FormQuantityInput = ({ showFree, walletFree, portfolioFree, ticker, onChange, disabled }) => {
  const form = Form.useFormInstance();

  const freeAmount = (() => {
    if (!showFree) return undefined;

    if (exists(walletFree) && exists(portfolioFree)) {
      return Math.min(walletFree, portfolioFree);
    }
    else if (exists(walletFree)) {
      return walletFree;
    }
    else if (exists(portfolioFree)) {
      return portfolioFree;
    }
    return 0;
  })();

  const handlePasteMax = () => {
    form.setFieldValue('quantity', freeAmount);
    if (onChange) onChange();
  };

  // Правила валидации
  const rules = [{ required: true, message: 'Введите количество' }];

  // Добавляем правило максимального значения только если freeAmount определен
  if (exists(freeAmount)) {
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
          {showFree && freeAmount > 0 && (
            <Button type="link" onClick={handlePasteMax} style={{ padding: 0, marginLeft: 'auto' }}>MAX</Button>
          )}
        </div>
      }
      label={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <span>Количество</span>
        </div>
      }
      name="quantity"
      rules={rules}
    >
      <InputNumber
        addonBefore={ticker || '—'}
        placeholder="0.00"
        // step="0.00001"
        // min="0.00001"
        max={freeAmount}
        // precision={5}
        style={{ width: '100%' }}
        disabled={disabled}
        onChange={onChange}
      />
    </Form.Item>
  );
};

export default FormQuantityInput;
