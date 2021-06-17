import { FeatureMetadata, FeatureSummary } from 'interfaces/Feature';

export const featureSummary: FeatureSummary = {
  key: 'test key',
  name: 'test feature name',
  version: '1.02.0',
  availability: ['source 1', 'source 2'],
  entity: ['entity 1', 'entity 2'],
  description: 'test feature description',
};

export const featureMetadata: FeatureMetadata = {
  key: 'test key',
  name: 'test feature name',
  version: '1.02.0',
  status: 'status',
  feature_group: 'feature group',
  entity: ['entity 1', 'entity 2'],
  data_type: 'string',
  availability: ['source 1', 'source 2'],
  description: 'test feature description',
  owners: [
    {
      display_name: 'test',
      email: 'test@email.com',
      profile_url: 'profile_url',
      user_id: 'user_id',
    },
  ],
  badges: [],
  owner_tags: [],
  tags: [],
  programmatic_descriptions: [],
  watermarks: [],
  stats: [],
  last_updated_timestamp: 0,
  created_timestamp: 0,
};
