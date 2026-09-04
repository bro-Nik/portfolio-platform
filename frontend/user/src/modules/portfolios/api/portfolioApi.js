import { getPortfolios } from 'src/api';

const portfolios = getPortfolios();

export const portfolioApi = {
  savePortfolio: (portfolioData) => {
    if (portfolioData.id) {
      return portfolios.updatePortfolioApiPortfoliosPortfolioIdPut(portfolioData.id, portfolioData);
    }
    return portfolios.createPortfolioApiPortfoliosPost(portfolioData);
  },
  deletePortfolio: (portfolioId) => portfolios.deletePortfolioApiPortfoliosPortfolioIdDelete(portfolioId),
  setPortfolioArchived: (portfolioId, isArchived) =>
    portfolios.setPortfolioArchivedApiPortfoliosPortfolioIdPatch(portfolioId, { isArchived }),
  getAssetTransactions: (portfolioId, assetId) =>
    portfolios.getAssetTransactionsApiPortfoliosPortfolioIdAssetsAssetIdTransactionsGet(portfolioId, assetId),
  addAssetToPortfolio: (portfolioId, tickerId) =>
    portfolios.addAssetToPortfolioApiPortfoliosPortfolioIdAssetsPost(portfolioId, { tickerId, portfolioId }),
  delAssetFromPortfolio: (portfolioId, assetId) =>
    portfolios.deleteAssetFromPortfolioApiPortfoliosPortfolioIdAssetsAssetIdDelete(portfolioId, assetId),
  setAssetArchived: (portfolioId, assetId, isArchived) =>
    portfolios.setAssetInPortfolioArchivedApiPortfoliosPortfolioIdAssetsAssetIdPatch(portfolioId, assetId, { isArchived }),
};
