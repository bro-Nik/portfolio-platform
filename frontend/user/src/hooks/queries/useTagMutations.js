import { useMutation, useQueryClient } from '@tanstack/react-query';
import { tagApi } from '../../modules/portfolios/api/tagApi';

export const useTagMutations = () => {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['tags'] });
  };

  const createTag = useMutation({
    mutationFn: ({ name, color }) => tagApi.createTag(name, color),
    onSuccess: () => invalidate(),
  });

  const updateTag = useMutation({
    mutationFn: ({ tagId, data }) => tagApi.updateTag(tagId, data),
    onSuccess: () => invalidate(),
  });

  const deleteTag = useMutation({
    mutationFn: (tagId) => tagApi.deleteTag(tagId),
    onSuccess: () => invalidate(),
  });

  const attachTag = useMutation({
    mutationFn: ({ tagId, entityType, entityId }) => tagApi.attachTag(tagId, entityType, entityId),
    onSuccess: () => invalidate(),
  });

  const detachTag = useMutation({
    mutationFn: ({ tagId, entityType, entityId }) => tagApi.detachTag(tagId, entityType, entityId),
    onSuccess: () => invalidate(),
  });

  return { createTag, updateTag, deleteTag, attachTag, detachTag };
};
