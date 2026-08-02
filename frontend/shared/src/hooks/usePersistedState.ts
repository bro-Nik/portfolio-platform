import { useState, useCallback } from 'react';
import { useAuthStore } from '../stores/authStore.js';

const readValue = <T>(key: string, defaultValue: T): T => {
  try {
    const stored = localStorage.getItem(key);
    return stored !== null ? (JSON.parse(stored) as T) : defaultValue;
  } catch {
    return defaultValue;
  }
};

export const usePersistedState = <T>(
  key: string | undefined,
  defaultValue: T,
): [T, (value: T | ((prev: T) => T)) => void] => {
  const userId = useAuthStore((state) => state.user?.id);
  const scopedKey = key ? (userId ? `${key}-${userId}` : key) : undefined;

  const [state, setState] = useState<T>(() =>
    scopedKey ? readValue(scopedKey, defaultValue) : defaultValue,
  );

  const [prevScopedKey, setPrevScopedKey] = useState(scopedKey);
  if (prevScopedKey !== scopedKey) {
    setPrevScopedKey(scopedKey);
    setState(scopedKey ? readValue(scopedKey, defaultValue) : defaultValue);
  }

  const setPersistedState = useCallback(
    (value: T | ((prev: T) => T)) => {
      setState(prev => {
        const newValue = typeof value === 'function' ? (value as (prev: T) => T)(prev) : value;
        if (scopedKey) localStorage.setItem(scopedKey, JSON.stringify(newValue));
        return newValue;
      });
    },
    [scopedKey],
  );

  return [state, setPersistedState];
};
