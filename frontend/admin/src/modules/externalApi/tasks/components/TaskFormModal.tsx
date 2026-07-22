import { useEffect } from 'react';
import { Modal, Form, Input, Switch, Select, Space, Button } from 'antd';
import { schedulePresets } from '../constants';

import { useModalStore } from '@portfolio/shared';
import { useTaskActions } from '../hooks/useTaskActions';
import { Task, TaskFormData } from '../../../../types/task';
import { useProvidersWithMethods } from '../../providers/hooks/useProviders';
import { DynamicParametersForm } from './DynamicParametersForm';

interface TaskFormModalProps { task?: Task }

const { Option } = Select;

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

  const activeProviders = providers.filter(p => p.isActive);
  const currentProviderInactive = editMode && task?.providerName && !activeProviders.find(p => p.name === task.providerName);
  const selectableProviders = currentProviderInactive
    ? providers.filter(p => p.isActive || p.name === task?.providerName)
    : activeProviders;

  const getInitialValues = () => {
    if (!task) return DEFAULT_VALUES;
    return {
      ...DEFAULT_VALUES,
      ...task,
      parameters: typeof task.parameters === 'string'
        ? JSON.parse(task.parameters)
        : task.parameters || {},
    };
  };

  const selectedProviderName = Form.useWatch('providerName', form);
  const selectedProvider = providers.find(p => p.name === selectedProviderName);

  const availableTaskTypes = selectedProvider?.methods?.map(m => ({
    value: m.method,
    label: m.name,
    exampleParams: m.exampleParams,
    parametersSchema: m.parametersSchema,
  })) || [];

  const selectedTaskType = Form.useWatch('taskType', form);
  const selectedMethod = availableTaskTypes.find(t => t.value === selectedTaskType);

  useEffect(() => {
    if (selectedMethod?.exampleParams) {
      form.setFieldValue('parameters', selectedMethod.exampleParams);
    }
  }, [selectedMethod, form]);

  const handleSubmit = (values: TaskFormData) => {
    if (editMode && task) {
      updateTask(task.id, values);
    } else {
      createTask(values);
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
      destroyOnHidden
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
            notFoundContent={
              providersLoading ? 'Загрузка...' : 'Нет активных провайдеров. Сначала настройте провайдера.'
            }
          >
            {selectableProviders.map(provider => (
              <Option key={provider.name} value={provider.name}>
                {provider.name}
              </Option>
            ))}
          </Select>
        </Form.Item>

        {currentProviderInactive && (
          <div style={{
            marginBottom: 16,
            padding: '8px 12px',
            background: '#fff7e6',
            borderRadius: '6px',
            borderLeft: '3px solid #faad14',
            fontSize: '13px',
            color: '#ad6800',
          }}>
            Текущий провайдер &laquo;{task?.providerName}&raquo; неактивен. Задача продолжит работу, но для новых задач выберите другого провайдера.
          </div>
        )}

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

        <Form.Item label="Параметры задачи">
          <DynamicParametersForm schema={selectedMethod?.parametersSchema || []} />
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
