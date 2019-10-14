export enum NotificationType {
  OWNER_ADDED = 'owner_added',
  OWNER_REMOVED = 'owner_removed',
  METADATA_EDITED = 'metadata_edited',
  METADATA_REQUESTED = 'metadata_requested',
}

export enum RequestMetadataType {
  COLUMN_DESCRIPTION = 'columnDescriptionRequested',
  TABLE_DESCRIPTION = 'tableDescriptionRequested',
}

export interface SendNotificationOptions {
  resource_name: string,
  resource_path: string,
  description_requested: boolean,
  fields_requested: boolean,
  comment?: string,
};
