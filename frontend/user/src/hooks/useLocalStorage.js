import { useState, useCallback } from 'react';

export const useLocalStorage = (key, initialValue) => {
  const hasKey = key && key.length > 0;
  const [storedValue, setStoredValue] = useState(() => {
    if (!hasKey) return initialValue;
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback((value) => {
    setStoredValue(prev => {
      const newValue = typeof value === 'function' ? value(prev) : value;
      if (hasKey) localStorage.setItem(key, JSON.stringify(newValue));
      return newValue;
    });
  }, [key, hasKey]);

  return [storedValue, setValue];
};
