// Валюта представления пользователя.
// Пока жёстко USD; в будущем — настройка пользователя (здесь появится курс).
export const DISPLAY_CURRENCY = 'USD';

// Из валюты представления в USD (для бэкенда)
export const toUsd = (value) => value;

// Из USD в валюту представления (для отображения)
export const fromUsd = (value) => value;
