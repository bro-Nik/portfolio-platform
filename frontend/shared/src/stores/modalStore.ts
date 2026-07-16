import { create } from 'zustand';
import type { ComponentType } from 'react';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyComponent = ComponentType<any>;

interface ModalState {
  currentModal: AnyComponent | null;
  modalProps: any;
  openModal: (modalComponent: AnyComponent, modalProps?: Record<string, any>) => void;
  closeModal: () => void;
}

export const useModalStore = create<ModalState>((set) => ({
  currentModal: null,
  modalProps: {},

  openModal: (modalComponent, modalProps = {}) => {
    set({
      currentModal: modalComponent,
      modalProps,
    });
  },

  closeModal: () => {
    set({
      currentModal: null,
      modalProps: {},
    });
  },
}));
