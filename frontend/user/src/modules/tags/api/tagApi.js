import { getTags } from 'src/api';

const tags = getTags();

export const tagApi = {
  getTags: () => tags.getTagsApiTagsGet(),

  createTag: (name, color, scope) => tags.createTagApiTagsPost({ name, color, scope }),

  updateTag: (tagId, data) => tags.updateTagApiTagsTagIdPut(tagId, data),

  deleteTag: (tagId) => tags.deleteTagApiTagsTagIdDelete(tagId),

  attachTag: (tagId, entityType, entityId) =>
    tags.attachTagApiTagsTagIdEntitiesEntityTypeEntityIdPost(tagId, entityType, entityId),

  detachTag: (tagId, entityType, entityId) =>
    tags.detachTagApiTagsTagIdEntitiesEntityTypeEntityIdDelete(tagId, entityType, entityId),
};
