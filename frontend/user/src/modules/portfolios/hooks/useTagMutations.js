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

export const useTagMutations = () => {
  const queryClient = useQueryClient();

  const createTag = useMutation({
    mutationFn: ({ name, color }) => tagApi.createTag(name, color),

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

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
    },
  });

  const updateTag = useMutation({
    mutationFn: ({ tagId, data }) => tagApi.updateTag(tagId, data),

    onMutate: async ({ tagId, data }) => {
      await Promise.all([
        queryClient.cancelQueries({ queryKey: ['tags'] }),
        queryClient.cancelQueries({ queryKey: ['portfolios'] }),
      ]);
      const previousTags = queryClient.getQueryData(['tags']);
      const previousPortfolios = queryClient.getQueryData(['portfolios']);

      queryClient.setQueryData(['tags'], (old) => {
        if (!old) return old;
        return old.map(t => t.id === tagId ? { ...t, ...data } : t);
      });

      queryClient.setQueryData(['portfolios'], (old) => {
        return updateTagInPortfolios(old, tagId, (tags) =>
          tags.map(t => t.id === tagId ? { ...t, ...data } : t)
        );
      });

      return { previousTags, previousPortfolios };
    },

    onSuccess: (serverTag, { tagId }) => {
      queryClient.setQueryData(['tags'], (old) => {
        if (!old) return old;
        return old.map(t => t.id === tagId ? serverTag : t);
      });
      queryClient.setQueryData(['portfolios'], (old) => {
        return updateTagInPortfolios(old, tagId, (tags) =>
          tags.map(t => t.id === tagId ? serverTag : t)
        );
      });
    },

    onError: (_err, _vars, context) => {
      if (context?.previousTags) {
        queryClient.setQueryData(['tags'], context.previousTags);
      }
      if (context?.previousPortfolios) {
        queryClient.setQueryData(['portfolios'], context.previousPortfolios);
      }
    },
  });

  const deleteTag = useMutation({
    mutationFn: (tagId) => tagApi.deleteTag(tagId),

    onMutate: async (tagId) => {
      await Promise.all([
        queryClient.cancelQueries({ queryKey: ['tags'] }),
        queryClient.cancelQueries({ queryKey: ['portfolios'] }),
      ]);
      const previousTags = queryClient.getQueryData(['tags']);
      const previousPortfolios = queryClient.getQueryData(['portfolios']);

      queryClient.setQueryData(['tags'], (old) => {
        if (!old) return old;
        return old.filter(t => t.id !== tagId);
      });

      queryClient.setQueryData(['portfolios'], (old) => {
        return updateTagInPortfolios(old, tagId, (tags) =>
          tags.filter(t => t.id !== tagId)
        );
      });

      return { previousTags, previousPortfolios };
    },

    onError: (_err, _vars, context) => {
      if (context?.previousTags) {
        queryClient.setQueryData(['tags'], context.previousTags);
      }
      if (context?.previousPortfolios) {
        queryClient.setQueryData(['portfolios'], context.previousPortfolios);
      }
    },
  });

  const attachTag = useMutation({
    mutationFn: ({ tagId, entityType, entityId }) =>
      tagApi.attachTag(tagId, entityType, entityId),

    onMutate: async ({ tagId, entityType, entityId, parentId }) => {
      if (!['portfolio', 'portfolio_asset'].includes(entityType)) return {};

      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      const previous = queryClient.getQueryData(['portfolios']);

      const tags = queryClient.getQueryData(['tags']);
      const tag = tags?.find(t => t.id === tagId);
      if (!tag) return { previous };

      queryClient.setQueryData(['portfolios'], (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p => {
            if (entityType === 'portfolio' && p.id === entityId) {
              const hasTag = p.tags?.some(t => t.id === tagId);
              return hasTag ? p : { ...p, tags: [...(p.tags || []), tag] };
            }
            if (entityType === 'portfolio_asset' && p.id === parentId) {
              return {
                ...p,
                assets: p.assets?.map(a =>
                  a.id === entityId
                    ? { ...a, tags: a.tags?.some(t => t.id === tagId) ? a.tags : [...(a.tags || []), tag] }
                    : a
                ),
              };
            }
            return p;
          }),
        };
      });

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['portfolios'], context.previous);
      }
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['wallets'] });
      queryClient.invalidateQueries({ queryKey: ['overview'] });
    },
  });

  const detachTag = useMutation({
    mutationFn: ({ tagId, entityType, entityId }) =>
      tagApi.detachTag(tagId, entityType, entityId),

    onMutate: async ({ tagId, entityType, entityId, parentId }) => {
      if (!['portfolio', 'portfolio_asset'].includes(entityType)) return {};

      await queryClient.cancelQueries({ queryKey: ['portfolios'] });
      const previous = queryClient.getQueryData(['portfolios']);

      queryClient.setQueryData(['portfolios'], (old) => {
        if (!old?.portfolios) return old;
        return {
          ...old,
          portfolios: old.portfolios.map(p => {
            if (entityType === 'portfolio' && p.id === entityId) {
              return { ...p, tags: p.tags?.filter(t => t.id !== tagId) };
            }
            if (entityType === 'portfolio_asset' && p.id === parentId) {
              return {
                ...p,
                assets: p.assets?.map(a =>
                  a.id === entityId
                    ? { ...a, tags: a.tags?.filter(t => t.id !== tagId) }
                    : a
                ),
              };
            }
            return p;
          }),
        };
      });

      return { previous };
    },

    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['portfolios'], context.previous);
      }
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['wallets'] });
      queryClient.invalidateQueries({ queryKey: ['overview'] });
    },
  });

  return { createTag, updateTag, deleteTag, attachTag, detachTag };
};
