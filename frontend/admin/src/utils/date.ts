/**
 * Форматирует дату в относительный формат (например: "5 мин назад", "Завтра", "Через 3 дн")
 * @param dateString - ISO строка с датой или null/undefined
 * @returns Отформатированная строка
 */
export const formatRelativeTime = (dateString: string | null | undefined): string => {
  if (!dateString) return 'Никогда';
  
  dateString = dateString.endsWith('Z') ? dateString : dateString + 'Z';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const isFuture = diffMs < 0;
  const absDiffMs = Math.abs(diffMs);
  
  const diffDays = Math.floor(absDiffMs / (1000 * 60 * 60 * 24));
  const diffHours = Math.floor(absDiffMs / (1000 * 60 * 60));
  const diffMinutes = Math.floor(absDiffMs / (1000 * 60));
  
  // Общее форматирование с учетом времени (прошлое/будущее)
  if (diffDays === 0) {
    if (diffHours === 0) {
      if (diffMinutes === 0) {
        return 'Сейчас';
      }
      return isFuture ? `Через ${diffMinutes} мин` : `${diffMinutes} мин назад`;
    }
    return isFuture ? `Через ${diffHours} ч` : `${diffHours} ч назад`;
  } else if (diffDays === 1) {
    return isFuture ? 'Завтра' : 'Вчера';
  } else if (diffDays < 7) {
    return isFuture ? `Через ${diffDays} дн` : `${diffDays} дн назад`;
  }
  
  // Для дат более недели назад/вперед
  if (isFuture && diffDays >= 7) {
    return `Через ${diffDays} дн`;
  }
  
  return date.toLocaleDateString();
};

/**
 * Форматирует время в секундах в читаемый формат (часы и минуты)
 * @param seconds - количество секунд
 * @returns Отформатированная строка (например: "2 ч 30 мин", "45 мин", "-" для меньше минуты)
 */
export const formatTimeSum = (seconds: number): string => {
  // Если меньше минуты
  if (seconds < 60) {
    return '-';
  }

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  // Если только минуты
  if (hours === 0) {
    return `${minutes} мин`;
  }

  // Если только часы
  if (hours >= 100) {
    return `${hours} ч`;
  }
  
  // Все остальные случаи - часы и минуты
  return `${hours} ч ${minutes} мин`;
};
