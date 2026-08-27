import { useModalStore } from '../stores/modalStore.js';

export const ModalContainer = () => {
  const { currentModal: ModalComponent, modalProps } = useModalStore();
  if (!ModalComponent) return null;
  return <ModalComponent {...modalProps} />;
};
