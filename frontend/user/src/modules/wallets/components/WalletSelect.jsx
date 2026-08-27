import React from 'react';
import { Button } from 'antd';
import { Plus } from 'lucide-react';
import FormSelect from 'src/features/forms/FormSelect';

const WalletSelect = ({ onAddWallet, options, ...props }) => (
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
          onClick={onAddWallet}
        >
          Добавить кошелек
        </Button>
      </>
    )}
  />
);

export default WalletSelect;
