import { createApi } from '@portfolio/shared';

const api = createApi('/api/tags', { useAuth: true });

export const tagApi = {
  getTags: () => api.get(''),

  createTag: (name, color) => api.post('', { name, color }),

  updateTag: (tagId, data) => api.put(`/${tagId}`, data),

  deleteTag: (tagId) => api.del(`/${tagId}`),

  attachTag: (tagId, entityType, entityId) => api.post('/attach', {
    tag_id: tagId,
    entity_type: entityType,
    entity_id: entityId,
  }),

  detachTag: (tagId, entityType, entityId) => api.del(`/detach?tag_id=${tagId}&entity_type=${entityType}&entity_id=${entityId}`),
};
