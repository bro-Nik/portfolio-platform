// import React, { useEffect } from 'react';
import { Form, Input } from 'antd';

const { TextArea } = Input;

const FormComment = ({ placeholder = null, max = null }) => {

  placeholder = placeholder ? placeholder : 'Дополнительная информация...';
  max = max ? max : 500

  return (
    <Form.Item
      label="Комментарий"
      name="comment"
      rules={[{ max: max, message: `Максимум ${max} символов` }]}
    >
      <TextArea
        placeholder={placeholder}
        rows={3}
        showCount
        maxLength={max}
      />
    </Form.Item>
  );
};

export default FormComment;
