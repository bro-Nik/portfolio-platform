import { useState, useCallback, useMemo } from 'react';
import { useOverviewQuery } from 'src/modules/portfolios/hooks/useOverviewQuery';
import { useAssetPricesQuery } from 'src/hooks/TickerContext';
import { useWalletsData } from 'src/modules/wallets/hooks/useWalletsData';
import { usePortfoliosData } from 'src/modules/portfolios/hooks/usePortfoliosData';
import { isCounterTransactionFn } from 'src/modules/transaction/utils/type';

export const useTransactionData = ({ tickerId, walletId, portfolioId, transaction, transactionType, form }) => {
  const { data: overviewData } = useOverviewQuery();
  const portfolios = overviewData?.portfolios || [];
  const wallets = overviewData?.wallets || [];

  const { getWallet } = useWalletsData();
  const { getPortfolio } = usePortfoliosData();
  const { data: pricesData } = useAssetPricesQuery();
  const prices = useMemo(() => pricesData?.prices || {}, [pricesData]);

  const isCounterTransaction = isCounterTransactionFn({ tickerId, walletId, portfolioId, transaction });

  const baseId = transaction?.tickerId || tickerId;

  const symbolMap = useMemo(() => {
    const map = {};
    portfolios.forEach(p => p.assets?.forEach(a => { map[a.tickerId] = a.symbol; }));
    wallets.forEach(w => w.assets?.forEach(a => { map[a.tickerId] = a.symbol; }));
    return map;
  }, [portfolios, wallets]);

  const baseTicker = useMemo(() => ({
    id: baseId,
    symbol: (transaction?.tickerSymbol || symbolMap[baseId])?.toUpperCase(),
    price: prices[baseId] || 0,
  }), [baseId, transaction?.tickerSymbol, symbolMap, prices]);

  const [quoteTicker, setQuoteTicker] = useState(() => {
    if (!transaction?.ticker2Id) return null;
    const symbol = transaction?.ticker2Symbol || symbolMap[transaction.ticker2Id];
    return {
      id: transaction.ticker2Id,
      symbol: symbol?.toUpperCase(),
      price: prices[transaction.ticker2Id] || 0,
    };
  });

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
  }, [calculatePortfolioAssetAvailableBalance]);

  const prepareSelectedWallet = useCallback((walletId) => {
    const wallet = walletId && getWallet(walletId);
    if (!wallet) return;

    return {
      ...wallet,
      baseAssetFree: getWalletAvailableBalanceByTicker(wallet, baseId),
      quoteAssetFree: getWalletAvailableBalanceByTicker(wallet, quoteTicker?.id),
      assets: wallet.assets.filter(a => a.tickerId !== baseId).map(a => ({
        ...a,
        free: calculateWalletAssetAvailableBalance(a, wallet),
        symbol: a.symbol?.toUpperCase(),
      }))
    };
  }, [getWallet, getWalletAvailableBalanceByTicker, calculateWalletAssetAvailableBalance, baseId, quoteTicker?.id]);

  const prepareSelectedPortfolio = useCallback((portfolioId) => {
    const portfolio = portfolioId && getPortfolio(portfolioId);
    if (!portfolio) return;

    return {
      ...portfolio,
      baseAssetFree: getPortfolioAvailableBalanceByTicker(portfolio, baseId),
    };
  }, [getPortfolio, getPortfolioAvailableBalanceByTicker, baseId]);

  const [transactionWallet, setTransactionWallet] = useState(() => {
    return prepareSelectedWallet(transaction ? transaction?.walletId : walletId)
  });

  const transactionPortfolio = prepareSelectedPortfolio(transaction ? transaction.portfolioId : portfolioId);

  const getPortfolios = useCallback(({ excludeId = null, showTickerId = null }) => {
    const currentPortfolioId = transaction?.portfolioId || portfolioId;
    let result = portfolios.filter(p => !p.isArchived || p.id === currentPortfolioId);
    if (excludeId) result = result.filter(p => p.id !== excludeId);

    if (showTickerId) {
      result = result.map(p => ({ ...p, free: getPortfolioAvailableBalanceByTicker(p, showTickerId) }));
    }

    return result;
  }, [portfolios, portfolioId, transaction?.portfolioId, getPortfolioAvailableBalanceByTicker]);

  const getWallets = useCallback(({ excludeId = null, showTickerId = null }) => {
    const currentWalletId = transaction?.walletId || walletId;
    let result = wallets.filter(w => !w.isArchived || w.id === currentWalletId);
    if (excludeId) result = result.filter(w => w.id !== excludeId);

    if (showTickerId) {
      result = result.map(w => ({ ...w, free: getWalletAvailableBalanceByTicker(w, showTickerId) }));
    }

    return result;
  }, [wallets, walletId, transaction?.walletId, getWalletAvailableBalanceByTicker]);

  const handleWalletChange = useCallback((walletId) => {
    setTransactionWallet(prepareSelectedWallet(walletId));
  }, [prepareSelectedWallet]);

  const handleQuoteTickerChange = useCallback((tickerId) => {
    const asset = transactionWallet?.assets?.find(a => a.tickerId === tickerId);
    const price = prices[tickerId] || 0;
    const newQuoteTicker = {
      id: tickerId,
      symbol: asset?.symbol?.toUpperCase(),
      price,
    };
    setQuoteTicker(newQuoteTicker);

    const wallet = {
      ...transactionWallet,
      quoteAssetFree: getWalletAvailableBalanceByTicker(transactionWallet, tickerId),
    };
    setTransactionWallet(wallet);

    const newPrice = price !== 0 ? baseTicker.price / price : 0;
    form.setFieldValue('price', newPrice || '');
  }, [transactionWallet, prices, getWalletAvailableBalanceByTicker, baseTicker.price, form]);

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
