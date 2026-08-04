import { Button } from 'antd';
import { Calendar, MessageSquare } from 'lucide-react';

const MetaRowGroup = ({ date, onDate, onComment }) => (
  <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
    {onDate && (
      <Button icon={<Calendar size={16} />} onClick={onDate}>
        {date?.format('DD.MM.YYYY HH:mm')}
      </Button>
    )}
    {onComment && (
      <Button icon={<MessageSquare size={16} />} onClick={onComment}>
        Комментарий
      </Button>
    )}
  </div>
);

export default MetaRowGroup;
