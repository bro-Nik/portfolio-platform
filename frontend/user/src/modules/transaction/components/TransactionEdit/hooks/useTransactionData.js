import { useState, useCallback } from 'react';
import { usePortfoliosQuery } from 'src/modules/portfolios/hooks/usePortfoliosQuery';
import { useWalletsQuery } from 'src/modules/wallets/hooks/useWalletsQuery';
import { useTicker } from 'src/hooks/useTicker';
import { useWalletsData } from 'src/modules/wallets/hooks/useWalletsData';
import { usePortfoliosData } from 'src/modules/portfolios/hooks/usePortfoliosData';
import { isCounterTransactionFn } from 'src/modules/transaction/utils/type';

export const useTransactionData = ({ tickerId, walletId, portfolioId, transaction, transactionType, form }) => {
  const { data: portfoliosData } = usePortfoliosQuery();
  const { data: walletsData } = useWalletsQuery();
  const portfolios = portfoliosData?.portfolios || [];
  const wallets = walletsData?.wallets || [];

  const { getWallet } = useWalletsData();
  const { getPortfolio } = usePortfoliosData();
  const { getTicker, getTickerSymbol } = useTicker();

  const isCounterTransaction = isCounterTransactionFn({ tickerId, walletId, portfolioId, transaction });

  const baseTicker = getTicker(transaction?.tickerId || tickerId);

  const [quoteTicker, setQuoteTicker] = useState(getTicker(transaction?.ticker2Id));

  const calculatePortfolioAssetAvailableBalance = useCallback((asset, portfolio) => {
    if (!asset) return 0;
    let free = asset?.quantity || 0;
    if (transaction
        && (asset.tickerId === transaction.tickerId || asset.tickerId === transaction.ticker2Id)
        && (portfolio.id === transaction.portfolioId || portfolio.id === transaction.portfolio2Id)
    ) free += +transaction.quantity * getTransactionQuantityDirection(transaction);
    return free;
  }, [transaction]);

  const calculateWalletAssetAvailableBalance = useCallback((asset, wallet) => {
    if (!asset) return 0;
    let free = asset?.quantity || 0;
    if (transaction
        && (asset.tickerId === transaction.tickerId || asset.tickerId === transaction.ticker2Id)
        && (wallet.id === transaction.walletId || wallet.id === transaction.wallet2Id)
    ) free += +transaction.quantity * getTransactionQuantityDirection(transaction);
    return free;
  }, [transaction]);

  const getWalletAvailableBalanceByTicker = useCallback((wallet, tickerId) => {
    if (!wallet || !tickerId) return 0;
    const asset = wallet?.assets?.find(a => a.tickerId === tickerId);
    if (asset) return calculateWalletAssetAvailableBalance(asset, wallet);
    return 0;
  }, [calculateWalletAssetAvailableBalance]);

  const getPortfolioAvailableBalanceByTicker = useCallback((portfolio, tickerId) => {
    if (!portfolio || !tickerId) return 0;
    const asset = portfolio?.assets?.find(a => a.tickerId === tickerId);
    if (asset) return calculatePortfolioAssetAvailableBalance(asset, portfolio);
    return 0;
  }, [calculatePortfolioAssetAvailableBalance, baseTicker?.id]);

  const prepareSelectedWallet = useCallback((walletId) => {
    const wallet = walletId && getWallet(walletId);
    if (!wallet) return;

    return {
      ...wallet,
      baseAssetFree: getWalletAvailableBalanceByTicker(wallet, baseTicker?.id),
      quoteAssetFree: getWalletAvailableBalanceByTicker(wallet, quoteTicker?.id),
      assets: wallet.assets.filter(a => a.tickerId !== baseTicker?.id).map(a => ({
        ...a,
        free: calculateWalletAssetAvailableBalance(a, wallet),
        symbol: getTickerSymbol(a.tickerId)
      }))
    };
  }, [getWallet, getTickerSymbol, getWalletAvailableBalanceByTicker, calculateWalletAssetAvailableBalance, baseTicker?.id]);

  const prepareSelectedPortfolio = useCallback((portfolioId) => {
    const portfolio = portfolioId && getPortfolio(portfolioId);
    if (!portfolio) return;

    return {
      ...portfolio,
      baseAssetFree: getPortfolioAvailableBalanceByTicker(portfolio, baseTicker?.id),
    };
  }, [getPortfolio, getPortfolioAvailableBalanceByTicker]);

  const [transactionWallet, setTransactionWallet] = useState(() => {
    return prepareSelectedWallet(transaction ? transaction?.walletId : walletId)
  });

  const transactionPortfolio = prepareSelectedPortfolio(transaction ? transaction.portfolioId : portfolioId);

  const getPortfolios = useCallback(({ excludeId = null, showTickerId = null }) => {
    let result = portfolios;
    if (excludeId) result = result.filter(p => p.id !== excludeId);

    if (showTickerId) {
      result = result.map(p => ({ ...p, free: getPortfolioAvailableBalanceByTicker(p, showTickerId) }));
    }

    return result;
  }, [portfolios, getPortfolioAvailableBalanceByTicker]);

  const getWallets = useCallback(({ excludeId = null, showTickerId = null }) => {
    let result = wallets;
    if (excludeId) result = result.filter(w => w.id !== excludeId);

    if (showTickerId) {
      result = result.map(w => ({ ...w, free: getWalletAvailableBalanceByTicker(w, showTickerId) }));
    }

    return result;
  }, [wallets, getWalletAvailableBalanceByTicker]);

  const handleWalletChange = useCallback((walletId) => {
    setTransactionWallet(prepareSelectedWallet(walletId));
  }, [prepareSelectedWallet]);

  const handleQuoteTickerChange = useCallback((tickerId) => {
    const newQuoteTicker = getTicker(tickerId);
    setQuoteTicker(newQuoteTicker);

    const wallet = {
      ...transactionWallet,
      quoteAssetFree: getWalletAvailableBalanceByTicker(transactionWallet, newQuoteTicker?.id),
    };
    setTransactionWallet(wallet);

    const price = newQuoteTicker?.price !== 0 ? baseTicker?.price / newQuoteTicker?.price : 0;
    form.setFieldValue('price', price || '');
  }, [getTicker, baseTicker?.price, form]);

  return {
    portfolios,
    handleWalletChange,
    transactionWallet,
    transactionPortfolio,
    isCounterTransaction,
    baseTicker,
    quoteTicker,
    handleQuoteTickerChange,
    getPortfolios,
    getWallets,
  };
};

const getTransactionQuantityDirection = (transaction) => {
  return ['Buy', 'Input', 'Earning', 'TransferIn'].includes(transaction.type) ? -1 : 1;
};
