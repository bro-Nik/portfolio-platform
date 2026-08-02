import { create } from 'zustand';
import type { ComponentType } from 'react';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyComponent = ComponentType<any>;

interface ModalState {
  currentModal: AnyComponent | null;
  modalProps: Record<string, unknown>;
  openModal: (modalComponent: AnyComponent, modalProps?: Record<string, unknown>) => void;
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

// Пропсы модалки типизируются на стороне потребителя (стор хранит их обобщённо)
export const useModalProps = <P extends object>(): P =>
  useModalStore((state) => state.modalProps) as P;
