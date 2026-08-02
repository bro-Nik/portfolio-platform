import { Modal, Divider, Card, Descriptions, Tag } from 'antd';
import { ApiOutlined } from '@ant-design/icons';
import { getTaskTypeTag, getStatusBadge } from '../utils';
import { useModalProps, useModalStore } from '@portfolio/shared';
import { Task } from '../../../../types/task';

interface TaskDetailsModalProps { task: Task }

export const TaskDetailsModal: React.FC = () => {
  const { closeModal } = useModalStore();
  const { task } = useModalProps<TaskDetailsModalProps>();

  if (!task) return null;

  return (
    <Modal
      title="Детали задачи"
      open={true}
      onCancel={closeModal}
      footer={null}
      width={800}
    >
      <div>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="Название" span={2}>
            {task.name}
          </Descriptions.Item>

          <Descriptions.Item label="Провайдер">
            <Tag icon={<ApiOutlined />} color="green">{task.providerName}</Tag>
          </Descriptions.Item>

          <Descriptions.Item label="Тип">
            {getTaskTypeTag(task.taskType)}
          </Descriptions.Item>

          <Descriptions.Item label="Статус">
            {getStatusBadge(task.isActive)}
          </Descriptions.Item>

          <Descriptions.Item label="Расписание">
            <Tag color="purple">{task.schedule}</Tag>
          </Descriptions.Item>

          <Descriptions.Item label="Последний запуск" span={2}>
            {task.lastRun ? new Date(task.lastRun).toLocaleString() : 'Никогда'}
          </Descriptions.Item>

          <Descriptions.Item label="Следующий запуск" span={2}>
            {task.nextRun ? new Date(task.nextRun).toLocaleString() : 'Не запланирован'}
          </Descriptions.Item>
        </Descriptions>

        <Divider titlePlacement="start">Параметры</Divider>

        <Card>
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
            {JSON.stringify(task.parameters, null, 2)}
          </pre>
        </Card>
      </div>
    </Modal>
  );
};
