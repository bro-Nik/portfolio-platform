import { Tooltip, theme } from 'antd';

const RichTooltip = ({ placement = 'top', ...props }) => {
  const { token } = theme.useToken();

  return (
    <Tooltip
      placement={placement}
      color={token.colorBgElevated}
      styles={{
        root: {
          maxWidth: 350,
          boxShadow: token.boxShadowSecondary,
        },
      }}
      {...props}
    />
  );
};

export default RichTooltip;
