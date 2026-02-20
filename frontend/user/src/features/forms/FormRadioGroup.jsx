import { Form, Radio, Segmented } from 'antd';

const FormRadioGroup = ({ name, btns, onChange }) => {

  return (
    <Form.Item name={name}>
      <Segmented
        options={btns}
        onChange={onChange}
      />
    </Form.Item>
  );
};

export default FormRadioGroup;
