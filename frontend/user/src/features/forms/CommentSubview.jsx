import { Button, Form, Input } from 'antd';
import SubviewHeader from 'src/components/ui/SubviewHeader';

const { TextArea } = Input;

const CommentSubview = ({ onClose }) => (
  <>
    <SubviewHeader title="Комментарий" onBack={onClose} />

    <Form.Item
      name="comment"
      rules={[{ max: 500, message: 'Максимум 500 символов' }]}
    >
      <TextArea
        placeholder="Дополнительная информация..."
        rows={4}
        showCount
        maxLength={500}
        autoFocus
        variant="filled"
      />
    </Form.Item>

    <Button type="primary" onClick={onClose} block>
      Добавить
    </Button>
  </>
);

export default CommentSubview;
