import { apiService } from '/app/src/services/api';
import { authService } from '/app/src/services/auth';

const { getValidToken } = authService();
const api = apiService('/api/tags', getValidToken);

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
