import React from 'react';
import { Form } from 'antd';
import PortfolioSelect from 'src/features/forms/PortfolioSelect';
import FormQuantityInput from 'src/features/forms/FormQuantityInput';

const PortfolioTransferFields = ({
  getPortfolios,
  fromPortfolio,
  baseTicker,
  isCounterTransaction,
  onCreatePortfolio,
}) => {

  const allPortfolios = getPortfolios({ excludeId: fromPortfolio?.id, showTickerId: baseTicker?.id });
  const portfolios = baseTicker?.market
    ? allPortfolios.filter(p => p.market === baseTicker.market || baseTicker.market === 'currency')
    : allPortfolios;
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
    <PortfolioSelect
      name='portfolio2Id'
      label='Портфель получатель'
      rules={[{ required: true, message: 'Выберите портфель' }]}
      hidden={isCounterTransaction}
      variant="filled"
      status={!portfolio2IdValue ? 'warning' : undefined}
      placeholder="Выберите портфель получатель"
      fieldNames={{label: 'name', value: 'id'}}
      options={portfolios}
      onCreatePortfolio={onCreatePortfolio}
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
