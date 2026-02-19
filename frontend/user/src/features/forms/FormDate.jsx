import { Form, Input } from 'antd';

const FormDate = () => {

  return (
    <Form.Item label="Дата" name="date"
      rules={[{ required: true, message: 'Введите дату' }]}
    >
      <Input type="datetime-local" />
    </Form.Item>
  );
};

export default FormDate;
