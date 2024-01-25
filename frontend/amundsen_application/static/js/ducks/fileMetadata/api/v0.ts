import axios, { AxiosResponse, AxiosError } from 'axios';

import {
  FileMetadata,
  User,
  Tag,
  ResourceType,
} from 'interfaces';

/** HELPERS **/
import {
  getFileQueryParams,
  getFileDataFromResponseData,
  shouldSendNotification,
} from './helpers';

const JSONBig = require('json-bigint');

export const API_PATH = '/api/metadata/v0';

type MessageAPI = { msg: string };

export type FileData = FileMetadata & {
  tags: Tag[];
};
export type DescriptionAPI = { description: string } & MessageAPI;
export type FileDataAPI = { fileData: FileData } & MessageAPI;

export function getFileData(key: string, index?: string, source?: string) {
  const fileQueryParams = getFileQueryParams({ key, index, source });
  const fileURL = `${API_PATH}/file?${fileQueryParams}`;
  const fileRequest = axios.get<FileDataAPI>(fileURL);

  return fileRequest.then((fileResponse: AxiosResponse<FileDataAPI>) => ({
    data: getFileDataFromResponseData(fileResponse.data),
    tags: fileResponse.data.fileData.tags,
    statusCode: fileResponse.status,
  }));
}

export function getFileDescription(fileData: FileMetadata) {
  const fileParams = getFileQueryParams({ key: fileData.key });

  return axios
    .get(`${API_PATH}/get_file_description?${fileParams}`)
    .then((response: AxiosResponse<DescriptionAPI>) => {
      fileData.description = response.data.description;

      return fileData;
    });
}

export function updateFileDescription(
  description: string,
  fileData: FileMetadata
) {
  return axios.put(`${API_PATH}/put_file_description`, {
    description,
    key: fileData.key,
    source: 'user',
  });
}




