import axios from 'axios';

import { GetPreviewDataRequest } from '../../tableMetadata/reducer';

const API_PATH = '/api/metadata/v0';
const sortTagsAlphabetical = (a, b) => a.tag_name.localeCompare(b.tag_name);

function getTableParams(tableDataObject) {
  const { cluster, database, schema, table_name } = tableDataObject;
  return `db=${database}&cluster=${cluster}&schema=${schema}&table=${table_name}`;
}

export function metadataPopularTables() {
  return axios.get(`${API_PATH}/popular_tables`).then((response) => {
    return response.data.results;
  })
  .catch((error) => {
    return error.response.data.results;
  });
}

export function metadataAllTags() {
  return axios.get(`${API_PATH}/tags`).then((response) => {
    return response.data.tags.sort(sortTagsAlphabetical);
  })
  .catch((error) => {
    return error.response.data.tags.sort(sortTagsAlphabetical);
  });
}

export function metadataTableTags(tableData) {
  const tableParams = getTableParams(tableData);

  return axios.get(`${API_PATH}/table?${tableParams}&index=&source=`).then((response) => {
    const newTableData = response.data.tableData;
    newTableData.tags = newTableData.tags.sort(sortTagsAlphabetical);
    return newTableData;
  })
  .catch((error) => {
    return tableData;
  });
}

export function metadataUpdateTableTags(action, tableData) {
  const updatePayloads = action.tagArray.map(tagObject => ({
      method: tagObject.methodName,
      url: `${API_PATH}/update_table_tags`,
      data: {
        cluster: tableData.cluster,
        db: tableData.database,
        schema: tableData.schema,
        table: tableData.table_name,
        tag: tagObject.tagName,
      },
    }
  ));
  return updatePayloads.map(payload => { axios(payload) })
}

export function metadataGetTableData(action) {
  const { searchIndex, source } = action;
  const tableParams = getTableParams(action);

  return axios.get(`${API_PATH}/table?${tableParams}&index=${searchIndex}&source=${source}`).then((response) => {
    const tableData = response.data.tableData;
    tableData.tags = tableData.tags.sort(sortTagsAlphabetical);
    return { tableData, statusCode: response.status };
  })
  .catch((error) => {
    return { tableData: {}, statusCode: error.response.status };
  });
}

export function metadataGetTableDescription(tableData) {
  const tableParams = getTableParams(tableData);
  return axios.get(`${API_PATH}/v0/get_table_description?${tableParams}`).then((response) => {
    tableData.table_description = response.data.description;
    return tableData;
  })
  .catch((error) => {
    return tableData;
  });
}

export function metadataUpdateTableDescription(description, tableData) {
  if (description.length === 0) {
    throw new Error();
  }
  else {
    return axios.put(`${API_PATH}/put_table_description`, {
      description,
      db: tableData.database,
      cluster: tableData.cluster,
      schema: tableData.schema,
      table: tableData.table_name,
      source: 'user',
    });
  }
}

export function metadataUpdateTableOwner(owner, method, tableData) {
  return axios({
    method,
    url: `${API_PATH}/update_table_owner`,
    data: {
      owner,
      db: tableData.database,
      cluster: tableData.cluster,
      schema: tableData.schema,
      table: tableData.table_name,
    }
  })
}

export function metadataGetColumnDescription(columnIndex, tableData) {
  const tableParams = getTableParams(tableData);
  const columnName = tableData.columns[columnIndex].name;
  return axios.get(`${API_PATH}/get_column_description?${tableParams}&column_name=${columnName}`).then((response) => {
    tableData.columns[columnIndex].description = response.data.description;
    return tableData;
  })
  .catch((error) => {
    return tableData;
  });
}

export function metadataUpdateColumnDescription(description, columnIndex, tableData) {
  if (description.length === 0) {
    throw new Error();
  }
  else {
    const columnName = tableData.columns[columnIndex].name;
    return axios.put(`${API_PATH}/put_column_description`, {
      description,
      db: tableData.database,
      cluster: tableData.cluster,
      column_name: columnName,
      schema: tableData.schema,
      table: tableData.table_name,
      source: 'user',
    });
  }
}

export function metadataGetLastIndexed() {
  return axios.get(`${API_PATH}/get_last_indexed`).then((response) => {
    return response.data.timestamp;
  });
}

export function metadataGetPreviewData(action: GetPreviewDataRequest) {
  return axios({
    url: '/api/preview/v0/',
    method: 'POST',
    data: action.queryParams,
  })
  .then((response) => {
    return { data: response.data.previewData, status: response.status };
  })
  .catch((error) => {
    return { data: {}, status: error.response.status };
  });
}
