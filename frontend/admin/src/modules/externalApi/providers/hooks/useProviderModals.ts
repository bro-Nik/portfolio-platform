import { useModalStore } from '@shared';
import { ProviderDelModal } from '../components/ProviderDelModal';
import { ProviderDetailsModal } from '../components/ProviderDetailsModal';
import { ProviderFormModal } from '../components/ProviderFormModal';
import { Provider } from '/app/src/types/provider';

export const useProviderModals = () => {
  const { openModal } = useModalStore();

  return {
    providerDetailsModal: (provider: Provider) => openModal(ProviderDetailsModal, { provider }),
    providerFormModal: (provider?: Provider) => openModal(ProviderFormModal, { provider }),
    providerDeleteConfirmModal: (provider: Provider) => openModal(ProviderDelModal, { provider }),
  };
};
