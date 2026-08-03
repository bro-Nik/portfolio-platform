export const getTickerImage = (ticker) => {
  if (!ticker?.image) return null;
  return import.meta.env.VITE_IMAGE_BASE_URL + ticker.market + '/24/' + ticker.image;
};

export const sortTransactions = (transactions) => {
  if (!transactions) return [];
  
  // Создаем копию массива, чтобы не мутировать оригинал
  const transactionsCopy = [...transactions];
  
  return transactionsCopy.sort((a, b) => {
    // Сначала ордеры (order: true) идут выше не-ордеров (order: false)
    if (a.order && !b.order) return -1;
    if (!a.order && b.order) return 1;
    
    // Если оба ордеры или оба не ордеры, сортируем по дате (свежие сверху)
    return new Date(b.date) - new Date(a.date);
  });
};
