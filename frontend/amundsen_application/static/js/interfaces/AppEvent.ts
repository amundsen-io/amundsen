import { Attribute } from './Attribute';

export interface AppEventMetaData {
  key: string;
  name: string;
  description: string;
  owned_by: string;
  label: string;
  action: string;
  category: string;
  source: string;
  vertical: string;
  last_updated_timestamp?: number;
  created_timestamp?: number;
  attributes: Array<Attribute>;
}
export interface AppEventSource {
  source: string | null;
  source_type: string;
}
