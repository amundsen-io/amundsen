// TODO: Remove notification types that can be triggered in flask layer if necessary
export enum NotificationType {
  OWNER_ADDED = 'added',
  OWNER_REMOVED = 'removed',
  METADATA_EDITED = 'edited',
  METADATA_REQUESTED = 'requested',
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
