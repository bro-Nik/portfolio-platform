import { Form, Input, InputNumber, Select, Switch } from 'antd';
import type { ParameterSchemaField } from '../../../../types/provider';

interface DynamicParametersFormProps {
  schema: ParameterSchemaField[];
}

export const DynamicParametersForm: React.FC<DynamicParametersFormProps> = ({ schema }) => {
  if (schema.length === 0) {
    return <div style={{ color: '#999', fontSize: 13 }}>Нет параметров</div>;
  }

  return (
    <>
      {schema.map((field) => (
        <Form.Item
          key={field.name}
          label={field.label}
          name={['parameters', field.name]}
          valuePropName={field.type === 'boolean' ? 'checked' : 'value'}
          rules={
            field.required
              ? [{ required: true, message: `Укажите ${field.label.toLowerCase()}` }]
              : undefined
          }
        >
          {field.type === 'select' ? (
            <Select placeholder={`Выберите ${field.label.toLowerCase()}`}>
              {Object.entries(field.options || {}).map(([value, label]) => (
                <Select.Option key={value} value={value}>
                  {label}
                </Select.Option>
              ))}
            </Select>
          ) : field.type === 'number' ? (
            <InputNumber
              style={{ width: '100%' }}
              placeholder={field.label}
            />
          ) : field.type === 'boolean' ? (
            <Switch />
          ) : (
            <Input placeholder={field.label} />
          )}
        </Form.Item>
      ))}
    </>
  );
};
