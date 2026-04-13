export const getErrorMessage = (error: unknown): string => {
  if (!error) return 'Произошла неизвестная ошибка';
  
  // Специальная обработка для Pydantic validation ошибок
  if (typeof error === 'object' && error !== null) {

    // Проверяем на Pydantic validation error
    if ('errors' in error && Array.isArray(error.errors)) {
      // Форматируем понятное сообщение
      const pydanticErrors = error.errors as Array<{type: string; loc: string[]; msg?: string}>;
      const missingFields = pydanticErrors.filter(e => e.type === 'missing').map(e => e.loc.join('.')).join(', ');
      
      if (missingFields) return `Не заполнены обязательные поля: ${missingFields}`;
      
      // Другие типы validation ошибок
      const firstError = pydanticErrors[0];
      if (firstError?.msg) return firstError.msg;
    }

    // ★ НОВАЯ ОБРАБОТКА: Парсинг строки с Pydantic ошибкой из поля message ★
    if ('message' in error && typeof error.message === 'string') {
      const msg = error.message;
      const fieldMatch = msg.match(/validation error for \S+\s+(\w+)\s+Field required/);
      if (fieldMatch && fieldMatch[1]) return `Не указано ${fieldMatch[1]}`;
      
      // Если распарсить не удалось, но сообщение похоже на validation error
      if (msg.includes('validation error') && msg.includes('Field required')) {
        return 'Проверьте правильность заполнения всех обязательных полей';
      }
      
      return msg;
    }
    
    // Стандартные поля ошибок
    if ('detail' in error && typeof error.detail === 'string') return error.detail;
    if ('message' in error && typeof error.message === 'string') return error.message;
    if ('error' in error && typeof error.error === 'string') return error.error;
  }
  
  if (error instanceof Error) return error.message;
  if (typeof error === 'string') return error;
  
  return 'Произошла ошибка при выполнении запроса';
};
