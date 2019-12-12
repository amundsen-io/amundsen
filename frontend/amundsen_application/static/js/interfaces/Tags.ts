import { UpdateMethod } from './Enums';

export interface UpdateTagData {
  methodName: UpdateMethod;
  tagName: string;
}

export enum TagType {
  TAG = 'default',
  BADGE = 'badge',
}

export interface Tag {
  tag_count?: number;
  tag_name: string;
  tag_type?: TagType.TAG;
}

export interface Badge {
  tag_name: string;
  tag_type: TagType.BADGE;
}
