import { ConfirmDeleteModal, useModalStore } from '@portfolio/shared';
import { usePortfolioOperations } from '../../hooks/usePortfolioOperations';

const PortfolioDeleteModal = () => {
  const { modalProps, closeModal } = useModalStore();
  const { portfolio } = modalProps;
  const { deletePortfolio } = usePortfolioOperations();

  return (
    <ConfirmDeleteModal
      entityName={portfolio.name}
      successMessage="Портфель удален"
      onConfirm={() => deletePortfolio(portfolio)}
      onCancel={closeModal}
    />
  );
};

export default PortfolioDeleteModal;
