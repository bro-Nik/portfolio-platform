import { Space, Form, Button } from 'antd';

const FormActionBtns = ({ title, disabled, onCancel, loading }) => {

  return (
    <Form.Item style={{ marginBottom: 0 }}>
      <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
        <Button onClick={onCancel}>
          Отмена
        </Button>
        <Button 
          type="primary" 
          htmlType="submit" 
          loading={loading}
          disabled={disabled}
        >
          {title || 'Ok'}
        </Button>
      </Space>
    </Form.Item>
  );
};

export default FormActionBtns;
