import React from 'react';
import { Form } from 'antd';
import FormSelect from 'src/features/forms/FormSelect';
import FormQuantityInput from 'src/features/forms/FormQuantityInput';

const PortfolioTransferFields = ({
  getPortfolios,
  fromPortfolio,
  baseTicker,
  isCounterTransaction,
}) => {

  const portfolios = getPortfolios({ excludeId: fromPortfolio?.id, showTickerId: baseTicker?.id });
  const form = Form.useFormInstance();
  const portfolio2IdValue = Form.useWatch('portfolio2Id', form);
  const quantityValue = Form.useWatch('quantity', form);

  return (
    <>

    {/* Портфель отправитель */}
    <Form.Item name="portfolioId" hidden initialValue={fromPortfolio?.id}>
      <input />
    </Form.Item>

    {/* Портфель получатель */}
    <FormSelect
      name='portfolio2Id'
      label='Портфель получатель'
      rules={[{ required: true, message: 'Выберите портфель' }]}
      hidden={isCounterTransaction}
      variant="filled"
      status={!portfolio2IdValue ? 'warning' : undefined}
      placeholder="Выберите портфель получатель"
      fieldNames={{label: 'name', value: 'id'}}
      options={portfolios}
      optionRender={(o) => (<>
        {o.data.name}
        <span className='option-subtext'>({o.data.free} {baseTicker?.symbol})</span>
      </>)}
    />

    {/* Количество */}
    <FormQuantityInput
      showFree={true}
      portfolioFree={fromPortfolio?.baseAssetFree}
      ticker={baseTicker?.symbol}
      status={portfolio2IdValue && !quantityValue ? 'warning' : undefined}
    />
    </>
  );
};

export default PortfolioTransferFields;
