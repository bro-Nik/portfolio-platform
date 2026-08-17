import { createApi } from '@portfolio/shared';

const api = createApi('/api/tags', { useAuth: true });

export const tagApi = {
  getTags: () => api.get(''),

  createTag: (name, color, scope) => api.post('', { name, color, scope }),

  updateTag: (tagId, data) => api.put(`/${tagId}`, data),

  deleteTag: (tagId) => api.del(`/${tagId}`),

  attachTag: (tagId, entityType, entityId) => api.post(`/${tagId}/entities/${entityType}/${entityId}`),

  detachTag: (tagId, entityType, entityId) => api.del(`/${tagId}/entities/${entityType}/${entityId}`),
};
