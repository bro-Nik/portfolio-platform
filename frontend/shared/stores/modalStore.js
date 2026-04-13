import { create } from 'zustand';

export const useModalStore = create((set, get) => ({
  currentModal: null,
  modalProps: {},
  
  openModal: (modalComponent, modalProps = {}) => {
    set({ 
      currentModal: modalComponent,
      modalProps 
    });
  },
  
  closeModal: () => {
    set({ 
      currentModal: null,
      modalProps: {} 
    });
  },
}));
