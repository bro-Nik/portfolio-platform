import React, { useEffect } from 'react';
import { Form } from 'antd';
import FormSelect from 'src/features/forms/FormSelect';
import FormQuantityInput from 'src/features/forms/FormQuantityInput';

const PortfolioTransferFields = ({
  getPortfolios,
  fromPortfolio,
  baseTicker,
  isCounterTransaction,
}) => {
  const form = Form.useFormInstance();

  useEffect(() => {
    form.setFieldsValue({ portfolioId: fromPortfolio?.id });
  }, [form, fromPortfolio?.id]);

  const portfolios = getPortfolios({ excludeId: fromPortfolio?.id, showTickerId: baseTicker?.id });

  return (
    <>

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
