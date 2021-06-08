import { FeatureResource, ResourceType } from 'interfaces';

export const featureSummary: FeatureResource = {
  type: ResourceType.feature,
  description: 'I am an ML feature',
  key: 'test_feature_group/test_feature_name/1.4',
  last_updated_timestamp: 946684799,
  name: 'test_feature_name',
  feature_group: 'test_feature_group',
  version: '1.4',
  availability: ['hive'],
  entity: 'test_entity',
  badges: [{ tag_name: 'pii' }],
};

export const featureMetadata = {
  type: ResourceType.feature,
  description: 'I am an ML feature',
  key: 'test_feature_group/test_feature_name/1.4',
  last_updated_timestamp: 946684799,
  name: 'test_feature_name',
  feature_group: 'test_feature_group',
  version: '1.4',
  availability: ['hive'],
  entity: 'test_entity',
  badges: [],
  tags: [],
  status: 'active',
  owners: [],
};
