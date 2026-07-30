import { Dropdown, Button } from 'antd';
import { MoreVertical } from 'lucide-react';

const ActionsDropdown = ({ items }) => (
  <Dropdown
    menu={{ items }}
    trigger={['click']}
    placement="bottomRight"
    autoFocus
  >
    <Button type="text" icon={<MoreVertical size={16} />} />
  </Dropdown>
);

export default ActionsDropdown;
