import React from 'react';
import { Form } from 'antd';
import FormSelect from '/app/src/features/forms/FormSelect';
import FormQuantityInput from '/app/src/features/forms/FormQuantityInput';

const PortfolioTransferFields = ({
  getPortfolios,
  fromPortfolio,
  baseTicker,
  isCounterTransaction,
}) => {
  const portfolios = getPortfolios({ excludeId: fromPortfolio?.id, showTickerId: baseTicker?.id });

  return (
    <>
    {/* Портфель отправитель */}
    <Form.Item name="portfolioId" hidden initialValue={fromPortfolio?.id}></Form.Item>

    {/* Портфель получатель */}
    <FormSelect
      name='portfolio2Id'
      label='Портфель получатель'
      rules={[{ required: true, message: 'Выберите портфель' }]}
      hidden={isCounterTransaction}
      fieldNames={{label: 'name', value: 'id'}}
      options={portfolios}
      optionRender={(o, { index }) => (<>
        {o.data.name}
        <span className='option-subtext'>({o.data.free} {baseTicker?.symbol})</span>
      </>)}
    />

    {/* Количество */}
    <FormQuantityInput
      showFree={true}
      portfolioFree={fromPortfolio?.baseAssetFree}
      ticker={baseTicker?.symbol}
    />
    </>
  );
};

export default PortfolioTransferFields;
