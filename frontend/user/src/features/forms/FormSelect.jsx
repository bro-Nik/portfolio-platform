import { Form, Select } from 'antd';
import { ChevronDownIcon } from '@heroicons/react/16/solid'

const FormSelect = ({
  name,
  label,
  value,
  rules,
  noStyle,
  hidden,
  ...props
}) => {

  return (
    <Form.Item 
      name={name}
      label={label} 
      initialValue={value}
      rules={rules}
      noStyle={noStyle}
      hidden={hidden}
    >
      <Select
        suffixIcon={<ChevronDownIcon />}
        // optionLabelProp="label"
        {...props}
      />
    </Form.Item>
  );
};

export default FormSelect;
