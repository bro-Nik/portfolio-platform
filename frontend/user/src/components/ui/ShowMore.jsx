import React, { useState, useCallback } from 'react';
import { Button } from 'antd';
import { PlusOutlined, MinusOutlined } from '@ant-design/icons';

const ShowMore = ({ content, show = false }) => {

  const [showMore, setShowMore] = useState(show);
  const toggleShowMore = useCallback(() => setShowMore(prev => !prev), []);

  return (
    <>
    <Button 
      type="link" 
      icon={showMore ? <MinusOutlined /> : <PlusOutlined />}
      onClick={toggleShowMore}
      style={{ padding: 0, height: 'auto' }}
    >
      {showMore ? 'Скрыть' : 'Еще'}
    </Button>

    {/* Контент */}
    {showMore && content}
    </>
  );
};

export default ShowMore;
