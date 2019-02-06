import axios from 'axios';

import { GetPreviewDataRequest } from '../../preview/reducer';

export function getPreviewData(action: GetPreviewDataRequest) {
  return axios({
    url:'/api/preview',
    method: 'POST',
    data: action.queryParams,
  })
  .then((response) => {
    return { previewData: response.data.previewData, status: response.status };
  })
  .catch((error) => {
    return { previewData: error.response.data.previewData, status: error.response.status };
  });
}
