import { createApi } from '@portfolio/shared';

const api = createApi('/api/tags', { useAuth: true });

export const tagApi = {
  getTags: () => api.get(''),

  createTag: (name, color, scope) => api.post('', { name, color, scope }),

  updateTag: (tagId, data) => api.put(`/${tagId}`, data),

  deleteTag: (tagId) => api.del(`/${tagId}`),

  attachTag: (tagId, entityType, entityId) => api.post('/attach', { tagId, entityType, entityId }),

  detachTag: (tagId, entityType, entityId) => api.del(`/detach?tag_id=${tagId}&entity_type=${entityType}&entity_id=${entityId}`),
};
