import React from 'react';
import { XMarkIcon, MinusIcon } from '@heroicons/react/24/solid'
import { useNavigation } from '/app/src/hooks/useNavigation';

const CloseMinimizeBtns = ({ id, type, parentId }) => {
  const { closeItem, minimizeItem } = useNavigation();

  return (
    <div class="close-minimize-btns">
      <div 
        onClick={() => minimizeItem(id, type, parentId)}
        title="Свернуть"
      >
        <MinusIcon />
      </div>

      <div 
        onClick={() => closeItem(id, type, parentId)}
        title="Закрыть"
      >
        <XMarkIcon />
      </div>
    </div>
  );
};

export default CloseMinimizeBtns;
