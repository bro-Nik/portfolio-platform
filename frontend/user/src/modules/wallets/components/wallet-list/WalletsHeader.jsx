import React from 'react';
import { useModalStore } from '/app/src/stores/modalStore';
import WalletEditModal from '../modals/WalletEdit';

const WalletsHeader = () => {
  const { openModal } = useModalStore();

  return (
    <div class="mb-5">
      <div class="row xs-mb-3">
        <div class="col-auto">
          <h1>Кошельки</h1>
        </div>
        <div class="col-auto ms-auto">
          <button className="btn btn-primary" onClick={() => openModal(WalletEditModal)} >
            Добавить кошелек
          </button>
        </div>
      </div>
    </div>
  );
};

export default WalletsHeader;
