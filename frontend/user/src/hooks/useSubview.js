import { useState, useCallback } from 'react';

export const useSubview = (initial = null) => {
  const [subview, setSubview] = useState(initial);
  const openSubview = useCallback((name) => setSubview(name), []);
  const closeSubview = useCallback(() => setSubview(null), []);

  return { subview, openSubview, closeSubview };
};
