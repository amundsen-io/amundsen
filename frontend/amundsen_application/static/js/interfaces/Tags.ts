import { UpdateMethod } from './Enums';

export interface UpdateTagData {
  methodName: UpdateMethod;
  tagName: string;
}

export interface Tag {
  tag_count: number;
  tag_name: string;
  tag_type?: string;
}
