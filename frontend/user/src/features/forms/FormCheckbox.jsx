import { Form, Checkbox } from 'antd';

const FormCheckbox = ({ label, checked, onChange }) => {

  return (
    <Form.Item name="order" valuePropName="checked">
      <Checkbox
        checked={checked}
        onChange={onChange}
      >
        {label}
      </Checkbox>
    </Form.Item>
  );
};

export default FormCheckbox;
