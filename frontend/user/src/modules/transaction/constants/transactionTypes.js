export const PORTFOLIO_TYPES = [
  { value: 'Buy', label: 'Покупка' },
  { value: 'Sell', label: 'Продажа' },
  { value: 'Input', label: 'Ввод' },
  { value: 'Output', label: 'Вывод' },
  { value: 'Earning', label: 'Заработок' },
  { value: 'TransferOut', label: 'Перевод' },
];

export const WALLET_TYPES = [
  { value: 'TransferOut', label: 'Перевод' },
];

export const TYPE_OPPOSITE_MAP = {
  'Buy': 'Sell',
  'Sell': 'Buy',
  'Input': 'Output',
  'Output': 'Input',
  'TransferIn': 'TransferOut',
  'TransferOut': 'TransferIn',
};

export const TYPE_NAME_MAP = {
  'Buy': 'Покупка',
  'Sell': 'Продажа',
  'Earning': 'Заработок',
  'Input': 'Ввод',
  'Output': 'Вывод',
  'TransferIn': 'Поступление',
  'TransferOut': 'Перевод',
};
