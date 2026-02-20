import { create } from 'zustand';

export const useModalStore = create((set, get) => ({
  // Текущая открытая модалка
  currentModal: null,
  modalProps: {},
  
  openModal: (modalComponent, modalProps = {}) => {
    set({ 
      currentModal: modalComponent,
      modalProps 
    });
  },
  
  // Закрыть модалку
  closeModal: () => {
    set({ 
      currentModal: null,
      modalProps: {} 
    });
  },
}));
