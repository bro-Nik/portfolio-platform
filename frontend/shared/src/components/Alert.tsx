import { Alert as AntAlert } from 'antd';
import type { AlertProps as AntAlertProps } from 'antd';

export type AlertProps = AntAlertProps;

export const Alert = (props: AlertProps) => (
  <AntAlert showIcon {...props} />
);
