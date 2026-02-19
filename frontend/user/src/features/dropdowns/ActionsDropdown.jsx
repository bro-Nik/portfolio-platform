import { Dropdown, Button } from 'antd';
import { MoreOutlined } from '@ant-design/icons';
import { ChevronDownIcon } from '@heroicons/react/16/solid'

const ActionsDropdown = ({ items, btn }) => {

  // EllipsisVerticalIcon
  const btns = {
    'icon': <Button type="text" icon={<MoreOutlined />} />,
    'btn': <Button type="default" icon={<ChevronDownIcon />}>Еще</Button>,
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
