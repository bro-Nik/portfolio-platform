import { useState, useCallback } from 'react';
import { useDataStore } from '/app/src/stores/dataStore';
import { useTicker } from '/app/src/hooks/useTicker';
import { useWalletsData } from '/app/src/modules/wallets/hooks/useWalletsData';
import { usePortfoliosData } from '/app/src/modules/portfolios/hooks/usePortfoliosData';
import { isCounterTransactionFn } from '/app/src/modules/transaction/utils/type';

export const useTransactionData = ({ tickerId, walletId, portfolioId, transaction, transactionType, form }) => {
  const portfolios = useDataStore(state => state.portfolios);
  const wallets = useDataStore(state => state.wallets);

  const { getWallet } = useWalletsData();
  const { getPortfolio } = usePortfoliosData();
  const { getTicker, getTickerSymbol } = useTicker();

  // Определение типа транзакции
  const isCounterTransaction = isCounterTransactionFn({ tickerId, walletId, portfolioId, transaction });

  // Базовый актив
  const baseTicker = getTicker(transaction?.tickerId || tickerId);

  // Котируемый актив
  const [quoteTicker, setQuoteTicker] = useState(getTicker(transaction?.ticker2Id));

  // Расчет доступного баланса актива портфеля с учетом текущей транзакции
  const calculatePortfolioAssetAvailableBalance = useCallback((asset, portfolio) => {
    if (!asset) return 0;
    let free = asset?.quantity || 0;
    if (transaction
        && (asset.tickerId === transaction.tickerId || asset.tickerId === transaction.ticker2Id)
        && (portfolio.id === transaction.portflioId || portfolio.id === transaction.portfolio2Id)
    ) free += +transaction.quantity * getTransactionQuantityDirection(transaction);
    return free;
  }, [transaction]);

  // Расчет доступного баланса актива кошелька с учетом текущей транзакции
  const calculateWalletAssetAvailableBalance = useCallback((asset, wallet) => {
    if (!asset) return 0;
    let free = asset?.quantity || 0;
    if (transaction
        && (asset.tickerId === transaction.tickerId || asset.tickerId === transaction.ticker2Id)
        && (wallet.id === transaction.walletId || wallet.id === transaction.wallet2Id)
    ) free += +transaction.quantity * getTransactionQuantityDirection(transaction);
    return free;
  }, [transaction]);

  // Получение доступного баланса тикера в кошельке
  const getWalletAvailableBalanceByTicker = useCallback((wallet, tickerId) => {
    if (!wallet || !tickerId) return 0;
    const asset = wallet?.assets?.find(a => a.tickerId === tickerId);
    if (asset) return calculateWalletAssetAvailableBalance(asset, wallet);
    return 0;
  }, [calculateWalletAssetAvailableBalance]);

  // Получение доступного баланса тикера в портфеле
  const getPortfolioAvailableBalanceByTicker = useCallback((portfolio, tickerId) => {
    if (!portfolio || !tickerId) return 0;
    const asset = portfolio?.assets?.find(a => a.tickerId === tickerId);
    if (asset) return calculatePortfolioAssetAvailableBalance(asset, portfolio);
    return 0;
  }, [calculatePortfolioAssetAvailableBalance, baseTicker?.id]);

  // Подготовка данных кошелька с рассчитанными балансами
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

  // Подготовка данных портфеля с рассчитанными балансами
  const prepareSelectedPortfolio = useCallback((portfolioId) => {
    const portfolio = portfolioId && getPortfolio(portfolioId);
    if (!portfolio) return;

    return {
      ...portfolio,
      baseAssetFree: getPortfolioAvailableBalanceByTicker(portfolio, baseTicker?.id),
    };
  }, [getPortfolio, getPortfolioAvailableBalanceByTicker]);

  // Кошелек для расчетов и получения перевода
  const [transactionWallet, setTransactionWallet] = useState(() => {
    return prepareSelectedWallet(transaction ? transaction?.walletId : walletId)
  });

  // Портфель для расчетов и для отправки перевода
  const transactionPortfolio = prepareSelectedPortfolio(transaction ? transaction.portfolioId : portfolioId);

  // Получение списка портфелей с опциональными фильтрами
  const getPortfolios = useCallback(({ excludeId = null, showTickerId = null }) => {
    let result = portfolios;
    if (excludeId) result = result.filter(p => p.id !== excludeId);

    if (showTickerId) {
      result = result.map(p => ({ ...p, free: getPortfolioAvailableBalanceByTicker(p, showTickerId) }));
    }

    return result;
  }, [portfolios, getPortfolioAvailableBalanceByTicker]);

  // Получение списка кошельков с опциональными фильтрами
  const getWallets = useCallback(({ excludeId = null, showTickerId = null }) => {
    let result = wallets;
    if (excludeId) result = result.filter(w => w.id !== excludeId);

    if (showTickerId) {
      result = result.map(w => ({ ...w, free: getWalletAvailableBalanceByTicker(w, showTickerId) }));
    }

    return result;
  }, [wallets, getWalletAvailableBalanceByTicker]);

  // Обработчик изменения выбранного кошелька
  const handleWalletChange = useCallback((walletId) => {
    setTransactionWallet(prepareSelectedWallet(walletId));
  }, [prepareSelectedWallet]);

  // Обработчик изменения котируемого тикера
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

// Вспомогательная функция для определения направления изменения количества в транзакции
export const getTransactionQuantityDirection = (transaction) => {
  return ['Buy', 'Input', 'Earning', 'TransferIn'].includes(transaction.type) ? -1 : 1;
};
