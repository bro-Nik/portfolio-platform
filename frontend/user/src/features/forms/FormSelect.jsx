import { Form, Select } from 'antd';

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
        {...props}
      />
    </Form.Item>
  );
};

export default FormSelect;
