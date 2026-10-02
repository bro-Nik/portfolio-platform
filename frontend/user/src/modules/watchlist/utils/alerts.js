export const DIRECTION_LABELS = {
  above: 'Выше',
  below: 'Ниже',
};

/** Направление из текущей цены — зеркалит серверный _derive_direction. */
export const deriveDirection = (currentPrice, targetPriceUsd) => {
  const current = Number(currentPrice);
  const target = Number(targetPriceUsd);
  if (!current || current <= 0 || !target || target <= 0) return null;
  return current >= target ? 'below' : 'above';
};

/** Доля пути до цели: 0 — цена на пороге, 1 — вдвое дальше. Null при битых данных. */
export const distanceToTarget = (currentPrice, targetPriceUsd, direction) => {
  const current = Number(currentPrice);
  const target = Number(targetPriceUsd);
  if (!current || current <= 0 || !target || target <= 0) return null;
  if (direction === 'above') {
    if (current >= target) return 0;
    return (target - current) / current;
  }
  if (direction === 'below') {
    if (current <= target) return 0;
    return (current - target) / current;
  }
  return null;
};

export const isTriggered = (alert) => Boolean(alert && !alert.isActive && alert.triggeredAt);
