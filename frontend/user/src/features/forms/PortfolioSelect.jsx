import React from 'react';
import { Button } from 'antd';
import { Plus } from 'lucide-react';
import FormSelect from './FormSelect';

const PortfolioSelect = ({ onCreatePortfolio, options, ...props }) => (
  <FormSelect
    {...props}
    options={options}
    popupRender={(menu) => (
      <>
        {menu}
        <Button
          type="dashed"
          block
          icon={<Plus size={14} />}
          style={{ marginTop: 8 }}
          onClick={onCreatePortfolio}
        >
          Создать портфель
        </Button>
      </>
    )}
  />
);

export default PortfolioSelect;
