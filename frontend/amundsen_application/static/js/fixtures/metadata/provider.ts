import {
  ProviderMetadata,
  DashboardResource,
} from '../../interfaces';

export const providerMetadata: ProviderMetadata = {
  description:
    'One row per ride request, showing all stages of the ride funnel. ',
  key: 'hive://gold.base/rides',
  name: 'rides',
  is_editable: true,
};