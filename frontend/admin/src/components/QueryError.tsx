import { Alert, Button } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';

interface QueryErrorProps {
  title?: string
  error: Error | null;
  onRetry?: () => void;
}

export const QueryError: React.FC<QueryErrorProps> = ({ title, error, onRetry }) => {
  if (!error) return null;
  
  return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      <Alert
        title={title || "Ошибка загрузки"}
        description={error.message}
        type="error"
        showIcon
        action={onRetry && (
          <Button size="small" icon={<ReloadOutlined />} onClick={onRetry}>
            Повторить
          </Button>
        )}
      />
    </div>
  );
};
