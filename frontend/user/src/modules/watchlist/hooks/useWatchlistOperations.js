import { useState } from 'react';
import { useWatchlistMutations } from './useWatchlistMutations';

const runMutation = async (setLoading, mutation, args) => {
  setLoading(true);
  try {
    const data = await mutation.mutateAsync(args);
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  } finally {
    setLoading(false);
  }
};

export const useWatchlistOperations = () => {
  const [loading, setLoading] = useState(false);
  const mutations = useWatchlistMutations();
  const run = (mutation, args) => runMutation(setLoading, mutation, args);

  const addItem = (ticker, comment) => run(mutations.addItem, { ticker, comment });
  const editItemComment = (id, comment) => run(mutations.editItem, { id, comment });
  const deleteItem = (id) => run(mutations.deleteItem, id);
  const archiveItem = (id, isArchived) => run(mutations.archiveItem, { id, isArchived });

  const saveAlert = (itemId, alert, data) => run(mutations.saveAlert, { itemId, alert, data });
  const deleteAlert = (alertId) => run(mutations.deleteAlert, alertId);
  const toggleAlert = (alertId, isActive) => run(mutations.toggleAlert, { alertId, isActive });

  return { addItem, editItemComment, deleteItem, archiveItem, saveAlert, deleteAlert, toggleAlert, loading };
};
