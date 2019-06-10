export enum UpdateTagMethod {
  DELETE = 'DELETE',
  PUT = 'PUT',
}

export interface UpdateTagData {
  methodName: UpdateTagMethod;
  tagName: string;
}
