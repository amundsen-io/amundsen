export interface Tag {
  tag_count: number;
  tag_name: string;
  tag_type?: string;
}

export enum UpdateTagMethod {
  DELETE = 'DELETE',
  PUT = 'PUT',
}

export interface UpdateTagData {
  methodName: UpdateTagMethod;
  tagName: string;
}
