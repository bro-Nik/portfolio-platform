import { useEffect } from 'react';
import { Modal, Form, Input, Switch, Select, Space, Button } from 'antd';
import { schedulePresets } from '../constants';
import { formatDescription } from '../utils';
import { useModalStore } from '@portfolio/shared';
import { useTaskActions } from '../hooks/useTaskActions';
import { Task, TaskFormData } from '../../../../types/task';
import { useProvidersWithMethods } from '../../providers/hooks/useProviders';

interface TaskFormModalProps { task?: Task }

const { Option } = Select;
const { TextArea } = Input;

const DEFAULT_VALUES: Partial<TaskFormData> = {
  schedule: '0 * * * *',
  isActive: true,
};

export const TaskFormModal: React.FC = () => {
  const { modalProps, closeModal } = useModalStore();
  const { task }: TaskFormModalProps = modalProps;
  const { createTask, updateTask, isCreating, isUpdating } = useTaskActions();

  const [form] = Form.useForm();
  const editMode = !!task?.id;

  const { data: providers = [], isLoading: providersLoading, error: providersError } = useProvidersWithMethods();

  const getInitialValues = () => {
    if (!task) return DEFAULT_VALUES;
    return {
      ...DEFAULT_VALUES,
      ...task,
      parameters: typeof task.parameters === 'string'
        ? task.parameters
        : JSON.stringify(task.parameters || {}, null, 2),
    };
  };

  const selectedProviderName = Form.useWatch('providerName', form);
  const selectedProvider = providers.find(p => p.name === selectedProviderName);

  const availableTaskTypes = selectedProvider?.methods?.map(m => ({
    value: m.method,
    label: m.name,
    description: m.description,
    exampleParams: m.exampleParams,
  })) || [];

  const selectedTaskType = Form.useWatch('taskType', form);
  const selectedMethod = availableTaskTypes.find(t => t.value === selectedTaskType);

  useEffect(() => {
    if (selectedMethod?.exampleParams) {
      form.setFieldValue('parameters', JSON.stringify(selectedMethod.exampleParams, null, 2));
    }
  }, [selectedMethod, form]);

  const handleSubmit = (values: TaskFormData) => {
    const taskData = {
      ...values,
      parameters: typeof values.parameters === 'string' ? JSON.parse(values.parameters) : values.parameters,
    };

    if (editMode && task) {
      updateTask(task.id, taskData);
    } else {
      createTask(taskData);
    }
    closeModal();
  };

  const handleCancel = () => {
    form.resetFields();
    closeModal();
  };

  const modalKey = task?.id || 'new';

  return (
    <Modal
      key={modalKey}
      title={editMode ? 'Редактирование задачи' : 'Создание новой задачи'}
      open={true}
      onCancel={handleCancel}
      footer={null}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={getInitialValues()}
      >
        <Form.Item
          label="Название задачи"
          name="name"
          rules={[{ required: true, message: 'Введите название задачи' }]}
        >
          <Input placeholder="Например: Ежечасное обновление цен" />
        </Form.Item>

        <Form.Item
          label="Провайдер (API)"
          name="providerName"
          help="Выберите поставщика данных"
          rules={[{ required: true, message: 'Выберите API провайдера' }]}
        >
          <Select
            placeholder="Выберите API провайдера"
            loading={providersLoading}
            disabled={!!providersError}
            showSearch
            optionFilterProp="children"
          >
            {providers.map(provider => (
              <Option key={provider.name} value={provider.name}>
                {provider.name}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          label="Тип задачи"
          name="taskType"
          rules={[{ required: true, message: 'Выберите тип задачи' }]}
        >
          <Select
            placeholder="Выберите тип задачи"
            disabled={!selectedProviderName}
            showSearch
            optionFilterProp="children"
          >
            {availableTaskTypes.map((type) => (
              <Option key={type.value} value={type.value}>
                {type.label}
              </Option>
            ))}
          </Select>
        </Form.Item>

        {selectedMethod?.description && (
          <div style={{
            marginBottom: 16,
            padding: '8px 12px',
            background: '#f0f5ff',
            borderRadius: '6px',
            borderLeft: '3px solid #1890ff',
          }}>
            <div style={{ fontSize: '13px', color: 'var(--text-admin-method)' }}>
              {formatDescription(selectedMethod.description)}
            </div>
          </div>
        )}

        <Form.Item
          label="Расписание"
          name="schedule"
        >
          <Select placeholder="Выберите расписание">
            {schedulePresets.map((preset) => (
              <Option key={preset.value} value={preset.value}>
                {preset.label}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          label="Параметры задачи (JSON)"
          name="parameters"
          rules={[
            { required: true, message: 'Введите параметры' },
            {
              validator: (_, value) => {
                try {
                  JSON.parse(value);
                  return Promise.resolve();
                } catch {
                  return Promise.reject(new Error('Неверный JSON формат'));
                }
              },
            },
          ]}
        >
          <TextArea rows={6} style={{ fontFamily: 'monospace' }} />
        </Form.Item>

        <Form.Item
          label="Активна"
          name="isActive"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>

        <Form.Item style={{ textAlign: 'right' }}>
          <Space>
            <Button onClick={handleCancel}>Отмена</Button>
            <Button type="primary" htmlType="submit" loading={isCreating || isUpdating}>Сохранить</Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
  );
};
