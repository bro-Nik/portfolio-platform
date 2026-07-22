import { KeyOutlined } from '@ant-design/icons';
import { useModalStore } from '@portfolio/shared';
import { Button, Col, Divider, Form, Input, InputNumber, Modal, Row, Space, Switch } from 'antd';
import { useProviderActions } from '../hooks/useProviderActions';
import { Provider, ProviderFormData } from '../../../../types/provider';

interface ProviderFormModalProps { provider?: Provider }

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

  const getInitialValues = () => {
    if (!provider) return DEFAULT_VALUES;
    return { ...DEFAULT_VALUES, ...provider };
  };

  const handleSubmit = (values: ProviderFormData) => {
    if (editMode) {
      updateProvider(provider!.name, values);
    } else {
      createProvider({ ...values, name: provider!.name });
    }
    closeModal();
  };

  const modalKey = provider?.id || provider?.name || 'new';

  return (
    <Modal
      key={modalKey}
      title={editMode ? `Редактировать ${provider?.name}` : `Настроить ${provider?.name || 'провайдера'}`}
      open={true}
      onCancel={closeModal}
      destroyOnHidden
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
          label={provider?.apiKeyRequired ? 'API Ключ (обязательно)' : 'API Ключ (опционально)'}
          name="apiKey"
          extra={provider?.apiKeyRequired ? undefined : 'Оставьте пустым, если не требуется'}
          rules={provider?.apiKeyRequired ? [{ required: true, message: 'Введите API ключ' }] : undefined}
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
