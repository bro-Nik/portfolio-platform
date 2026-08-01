import { useMutation, useQueryClient } from '@tanstack/react-query';
import { tagApi } from '../api/tagApi';

const replaceOptimisticId = (tags, optimisticId, newTag) => {
  return tags.map(t => t.id === optimisticId ? newTag : t);
};

const updateTagInPortfolios = (old, tagId, updater) => {
  if (!old?.portfolios) return old;
  return {
    ...old,
    portfolios: old.portfolios.map(p => ({
      ...p,
      tags: p.tags ? updater(p.tags) : p.tags,
      assets: p.assets?.map(a => ({
        ...a,
        tags: a.tags ? updater(a.tags) : a.tags,
      })),
    })),
  };
};

const updateTagInWallets = (old, tagId, updater) => {
  if (!old?.wallets) return old;
  return {
    ...old,
    wallets: old.wallets.map(w => ({
      ...w,
      tags: w.tags ? updater(w.tags) : w.tags,
      assets: w.assets?.map(a => ({
        ...a,
        tags: a.tags ? updater(a.tags) : a.tags,
      })),
    })),
  };
};

const updateTagInOverview = (old, tagId, updater) => {
  return updateTagInWallets(updateTagInPortfolios(old, tagId, updater), tagId, updater);
};

const applyTagChangeToStore = (old, { tag, tagId, entityType, entityId, parentId, action }) => {
  if (!old) return old;

  const updateTags = (tags) =>
    action === 'attach'
      ? (tags.some(t => t.id === tag.id) ? tags : [...tags, tag])
      : tags.filter(t => t.id !== tagId);

  const updateEntity = (entity) => {
    if (entityType === 'portfolio' && entity.id === entityId) {
      return { ...entity, tags: updateTags(entity.tags || []) };
    }
    if (entityType === 'portfolio_asset' && entity.id === parentId) {
      return {
        ...entity,
        assets: entity.assets?.map(a =>
          a.id === entityId ? { ...a, tags: updateTags(a.tags || []) } : a
        ),
      };
    }
    if (entityType === 'wallet' && entity.id === entityId) {
      return { ...entity, tags: updateTags(entity.tags || []) };
    }
    if (entityType === 'wallet_asset' && entity.id === parentId) {
      return {
        ...entity,
        assets: entity.assets?.map(a =>
          a.id === entityId ? { ...a, tags: updateTags(a.tags || []) } : a
        ),
      };
    }
    return entity;
  };

  if (entityType === 'portfolio' || entityType === 'portfolio_asset') {
    if (!old.portfolios) return old;
    return { ...old, portfolios: old.portfolios.map(updateEntity) };
  }
  if (entityType === 'wallet' || entityType === 'wallet_asset') {
    if (!old.wallets) return old;
    return { ...old, wallets: old.wallets.map(updateEntity) };
  }
  return old;
};

const optimisticTagChange = async (queryClient, { tagId, entityType, entityId, parentId, action }) => {
  await Promise.all([
    queryClient.cancelQueries({ queryKey: ['overview'] }),
    queryClient.cancelQueries({ queryKey: ['tags'] }),
  ]);

  const previous = queryClient.getQueryData(['overview']);

  const isPortfolioEntity = ['portfolio', 'portfolio_asset'].includes(entityType);
  const isWalletEntity = ['wallet', 'wallet_asset'].includes(entityType);
  if (!isPortfolioEntity && !isWalletEntity) return { previous };

  const tag = action === 'attach'
    ? queryClient.getQueryData(['tags'])?.find(t => t.id === tagId)
    : null;
  if (action === 'attach' && !tag) return { previous };

  const change = { tag, tagId, entityType, entityId, parentId, action };
  queryClient.setQueryData(['overview'], (old) => applyTagChangeToStore(old, change));

  return { previous };
};

const rollbackTagChange = (queryClient, previous) => {
  if (!previous) return;
  queryClient.setQueryData(['overview'], previous);
};

export const useTagMutations = () => {
  const queryClient = useQueryClient();

  const createTag = useMutation({
    mutationFn: ({ name, color, scope }) => tagApi.createTag(name, color, scope),

    onMutate: async ({ name, color }) => {
      await queryClient.cancelQueries({ queryKey: ['tags'] });
      const previous = queryClient.getQueryData(['tags']);
      const optimisticId = `optimistic-${Date.now()}`;

      queryClient.setQueryData(['tags'], (old) => {
        const newTag = { id: optimisticId, name, color: color || null };
        return old ? [...old, newTag] : [newTag];
      });

      return { previous, optimisticId };
    },

    onSuccess: (serverTag, _vars, context) => {
      queryClient.setQueryData(['tags'], (old) => {
        if (!old) return old;
        return replaceOptimisticId(old, context.optimisticId, serverTag);
      });
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['tags'], context.previous);
      }
    },
  });

  const updateTag = useMutation({
    mutationFn: ({ tagId, data }) => tagApi.updateTag(tagId, data),

    onMutate: async ({ tagId, data }) => {
      await Promise.all([
        queryClient.cancelQueries({ queryKey: ['tags'] }),
        queryClient.cancelQueries({ queryKey: ['overview'] }),
      ]);
      const previousTags = queryClient.getQueryData(['tags']);
      const previousOverview = queryClient.getQueryData(['overview']);

      queryClient.setQueryData(['tags'], (old) => {
        if (!old) return old;
        return old.map(t => t.id === tagId ? { ...t, ...data } : t);
      });

      const updater = (tags) => tags.map(t => t.id === tagId ? { ...t, ...data } : t);
      queryClient.setQueryData(['overview'], (old) => updateTagInOverview(old, tagId, updater));

      return { previousTags, previousOverview };
    },

    onSuccess: (serverTag, { tagId }) => {
      queryClient.setQueryData(['tags'], (old) => {
        if (!old) return old;
        return old.map(t => t.id === tagId ? serverTag : t);
      });

      const updater = (tags) => tags.map(t => t.id === tagId ? serverTag : t);
      queryClient.setQueryData(['overview'], (old) => updateTagInOverview(old, tagId, updater));
    },

    onError: (_err, _vars, context) => {
      if (context?.previousTags) {
        queryClient.setQueryData(['tags'], context.previousTags);
      }
      if (context?.previousOverview) {
        queryClient.setQueryData(['overview'], context.previousOverview);
      }
    },
  });

  const deleteTag = useMutation({
    mutationFn: (tagId) => tagApi.deleteTag(tagId),

    onMutate: async (tagId) => {
      await Promise.all([
        queryClient.cancelQueries({ queryKey: ['tags'] }),
        queryClient.cancelQueries({ queryKey: ['overview'] }),
      ]);
      const previousTags = queryClient.getQueryData(['tags']);
      const previousOverview = queryClient.getQueryData(['overview']);

      queryClient.setQueryData(['tags'], (old) => {
        if (!old) return old;
        return old.filter(t => t.id !== tagId);
      });

      const updater = (tags) => tags.filter(t => t.id !== tagId);
      queryClient.setQueryData(['overview'], (old) => updateTagInOverview(old, tagId, updater));

      return { previousTags, previousOverview };
    },

    onError: (_err, _vars, context) => {
      if (context?.previousTags) {
        queryClient.setQueryData(['tags'], context.previousTags);
      }
      if (context?.previousOverview) {
        queryClient.setQueryData(['overview'], context.previousOverview);
      }
    },
  });

  const attachTag = useMutation({
    mutationFn: ({ tagId, entityType, entityId }) =>
      tagApi.attachTag(tagId, entityType, entityId),

    onMutate: ({ tagId, entityType, entityId, parentId }) =>
      optimisticTagChange(queryClient, { tagId, entityType, entityId, parentId, action: 'attach' }),

    onError: (_err, _vars, context) => {
      rollbackTagChange(queryClient, context?.previous);
    },
  });

  const detachTag = useMutation({
    mutationFn: ({ tagId, entityType, entityId }) =>
      tagApi.detachTag(tagId, entityType, entityId),

    onMutate: ({ tagId, entityType, entityId, parentId }) =>
      optimisticTagChange(queryClient, { tagId, entityType, entityId, parentId, action: 'detach' }),

    onError: (_err, _vars, context) => {
      rollbackTagChange(queryClient, context?.previous);
    },
  });

  return { createTag, updateTag, deleteTag, attachTag, detachTag };
};
