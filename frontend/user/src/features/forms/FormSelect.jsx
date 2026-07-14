import { Form, Select } from 'antd';
import { ChevronDown } from 'lucide-react'

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
        suffixIcon={<ChevronDown size={14} />}
        {...props}
      />
    </Form.Item>
  );
};

export default FormSelect;
