import React from 'react';
import { useModalStore } from '/app/src/stores/modalStore';
import PortfolioEditModal from '../modals/PortfolioEdit';

const PortfoliosHeader = () => {
  const { openModal } = useModalStore();

  return (
    <div class="mb-5">
      <div class="row xs-mb-3">
        <div class="col-auto">
          <h1>Портфели</h1>
        </div>
        <div class="col-auto ms-auto">
          <button className="btn btn-primary" onClick={() => openModal(PortfolioEditModal)} >
            Добавить портфель
          </button>
        </div>
      </div>
    </div>
  );
};

export default PortfoliosHeader;
