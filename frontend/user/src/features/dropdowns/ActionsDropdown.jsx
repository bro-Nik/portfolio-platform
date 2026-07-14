import { Dropdown, Button } from 'antd';
import { MoreHorizontal, ChevronDown } from 'lucide-react';

const ActionsDropdown = ({ items, btn }) => {
  const btns = {
    'icon': <Button type="text" icon={<MoreHorizontal size={16} />} />,
    'btn': <Button type="default" icon={<ChevronDown size={16} />}>Еще</Button>,
  };

  const triggerBtn = btn ? btns[btn] : null;
  if (!triggerBtn) return;

  return (
    <Dropdown
      menu={{ items: items }}
      trigger={['click']}
      placement="bottomRight"
      autoFocus
    >
      {triggerBtn}
    </Dropdown>
  );
};

export default ActionsDropdown;
