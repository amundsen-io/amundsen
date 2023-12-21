import {
  ProviderMetadata,
  DashboardResource,
} from '../../interfaces';

export const providerMetadata: ProviderMetadata = {
  badges: [
    {
      badge_name: 'ga',
      category: 'table_status',
    },
  ],
  description:
    'One row per ride request, showing all stages of the ride funnel. ',
  key: 'hive://gold.base/rides',
  name: 'rides',
};
