import { ApiOutlined, KeyOutlined } from '@ant-design/icons';
import { useModalStore } from '@shared';
import { Button, Col, Divider, Form, Input, InputNumber, Modal, Row, Select, Space, Switch } from 'antd';
import { useEffect } from 'react';
import { useProviderActions } from '../hooks/useProviderActions';
import { useProvidersWithMethods } from '../hooks/useProviders';
import { Provider, ProviderFormData } from '/app/src/types/provider';

interface ProviderFormModalProps { provider?: Provider }

const { Option } = Select;

const DEFAULT_VALUES: Partial<ProviderFormData> = {
  retryDelay: 60,
  timeout: 30,
  isActive: true
};

export const ProviderFormModal: React.FC = () => {
  const { modalProps, closeModal } = useModalStore();
  const { provider }: ProviderFormModalProps = modalProps;
  const { createProvider, updateProvider, isCreating, isUpdating } = useProviderActions();

  const [form] = Form.useForm();
  const editMode = !!provider?.id;

  const { data: providers = [], isLoading: providersLoading, error: providersError } = useProvidersWithMethods();


  const getInitialValues = () => {
    if (!provider) return DEFAULT_VALUES;
    return { ...DEFAULT_VALUES, ...provider };
  };

  const selectedProviderName = Form.useWatch('name', form);

  useEffect(() => {
    if (!editMode && selectedProviderName) {
      const selectedProvider = providers.find(p => p.name === selectedProviderName);
      if (selectedProvider) {
        form.setFieldsValue({ ...DEFAULT_VALUES, ...selectedProvider });
      }
    }
  }, [selectedProviderName, providers, editMode, form]);

  const handleSubmit = (values: ProviderFormData) => {
    if (editMode) {
      updateProvider(provider.id, values);
    } else {
      createProvider(values);
    }
    closeModal();
  };

  const modalKey = provider?.id || 'new';

  return (
    <Modal
      key={modalKey}
      title={editMode ? 'Редактировать API провайдера' : 'Создать новый API провайдер'}
      open={true}
      onCancel={closeModal}
      footer={null}
      width={700}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={getInitialValues()}
      >
        <Form.Item
          label="Провайдер"
          name="name"
          rules={[{ required: true, message: 'Введите провайдера' }]}
        >
          <Select
            placeholder="Выберите провайдера"
            prefix={<ApiOutlined />}
            allowClear
            disabled={editMode || !!providersError}
            optionFilterProp="children"
            loading={providersLoading}
          >
            {providers.map(p => (
              <Option key={p.name} value={p.name}>
                {p.name}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          label="API Ключ (опционально)"
          name="apiKey"
          extra="Оставьте пустым, если не требуется"
        >
          <Input.Password 
            placeholder="Введите API ключ" 
            prefix={<KeyOutlined />}
          />
        </Form.Item>

        <Divider titlePlacement="start">Лимиты запросов</Divider>
        
        <Row gutter={16}>
          <Col span={6}>
            <Form.Item label="В минуту" name="requestsPerMinute">
              <InputNumber min={1} max={10000} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item label="В час" name="requestsPerHour">
              <InputNumber min={1} max={100000} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item label="В день" name="requestsPerDay">
              <InputNumber min={1} max={1000000} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item label="В месяц" name="requestsPerMonth">
              <InputNumber min={1} max={10000000} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              label="Таймаут (сек)"
              name="timeout"
              rules={[{ required: true, message: 'Введите таймаут' }]}
            >
              <InputNumber min={1} max={300} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              label="Задержка повтора (сек)"
              name="retryDelay"
              rules={[{ required: true, message: 'Введите задержку' }]}
            >
              <InputNumber min={1} max={3600} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          label="Активен"
          name="isActive"
          valuePropName="checked"
        >
          <Switch checkedChildren="Вкл" unCheckedChildren="Выкл" />
        </Form.Item>

        <Form.Item style={{ textAlign: 'right' }}>
          <Space>
            <Button onClick={closeModal}>Отмена</Button>
            <Button type="primary" htmlType="submit" loading={isCreating || isUpdating}>Сохранить</Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
  );
};
