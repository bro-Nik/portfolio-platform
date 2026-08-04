import { Button } from 'antd';
import { ArrowLeft } from 'lucide-react';

const SubviewHeader = ({ title, onBack }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
    <Button
      type="text"
      icon={<ArrowLeft size={18} />}
      onClick={onBack}
    />
    <div style={{ fontWeight: 600, fontSize: 16, color: 'var(--text-primary)' }}>{title}</div>
  </div>
);

export default SubviewHeader;
