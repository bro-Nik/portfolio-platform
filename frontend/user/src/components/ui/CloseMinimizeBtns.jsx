import React from 'react';
import { X, Minus } from 'lucide-react';
import { useNavigation } from '/app/src/hooks/useNavigation';

const CloseMinimizeBtns = ({ id, type, parentId }) => {
  const { closeItem, minimizeItem } = useNavigation();

  return (
    <div className="close-minimize-btns">
      <div 
        onClick={() => minimizeItem(id, type, parentId)}
        title="Свернуть"
      >
        <Minus size={14} />
      </div>

      <div 
        onClick={() => closeItem(id, type, parentId)}
        title="Закрыть"
      >
        <X size={14} />
      </div>
    </div>
  );
};

export default CloseMinimizeBtns;
