import React from 'react';
import { Divider, Button } from 'antd';
import { Plus } from 'lucide-react';
import FormSelect from './FormSelect';

const WalletSelect = ({ onAddWallet, options, ...props }) => (
  <FormSelect
    {...props}
    options={options}
    popupRender={(menu) => (
      <>
        {menu}
        <Divider style={{ margin: '4px 0' }} />
        <Button
          type="text"
          block
          size="small"
          icon={<Plus size={14} />}
          onClick={onAddWallet}
        >
          Добавить кошелек
        </Button>
      </>
    )}
  />
);

export default WalletSelect;
